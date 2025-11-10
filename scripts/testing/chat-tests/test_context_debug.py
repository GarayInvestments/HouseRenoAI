"""
Comprehensive Context Debug Test Script
Tests different query types to diagnose hallucination issues with smart context handler

This script sends various query types and then extracts debug logs to show:
1. What context_builder loaded (DEBUG logs)
2. What OpenAI received (OPENAI logs)
3. Whether data is present or missing
4. Where the disconnect happens

Run after deployment: commit 009da17 (debug logging added)
"""

import requests
import subprocess
import time
from datetime import datetime

BASE_URL = "https://houserenoai.onrender.com"
TEST_EMAIL = "test@houserenoai.com"
TEST_PASSWORD = "TestPass123!"

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_section(title):
    """Print formatted section header"""
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")

def print_test(number, description):
    """Print test header"""
    print(f"{Colors.OKCYAN}TEST {number}: {description}{Colors.ENDC}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def login():
    """Get auth token"""
    try:
        response = requests.post(
            f"{BASE_URL}/v1/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=10
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print_error(f"Login failed: {e}")
        return None

def get_actual_data(token):
    """Fetch actual data from Google Sheets via API"""
    try:
        print("\n📊 Fetching actual data from Google Sheets API...")
        
        clients = requests.get(
            f"{BASE_URL}/v1/clients",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        ).json()
        
        projects = requests.get(
            f"{BASE_URL}/v1/projects",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        ).json()
        
        permits = requests.get(
            f"{BASE_URL}/v1/permits",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        ).json()
        
        qb_status = requests.get(
            f"{BASE_URL}/v1/quickbooks/status",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        ).json()
        
        qb_customers = []
        if qb_status.get('authenticated'):
            qb_customers = requests.get(
                f"{BASE_URL}/v1/quickbooks/customers",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            ).json()
        
        print_success(f"Fetched {len(clients)} clients, {len(projects)} projects, {len(permits)} permits, {len(qb_customers)} QB customers")
        
        return {
            'clients': clients,
            'projects': projects,
            'permits': permits,
            'qb_customers': qb_customers,
            'qb_authenticated': qb_status.get('authenticated', False)
        }
    except Exception as e:
        print_error(f"Failed to fetch actual data: {e}")
        return None

def test_chat(token, message, session_id, test_num):
    """Send chat message and return response"""
    try:
        print(f"   Message: \"{message}\"")
        print(f"   Session: {session_id}")
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/v1/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": message, "session_id": session_id},
            timeout=60
        )
        elapsed = time.time() - start_time
        
        response.raise_for_status()
        result = response.json()
        
        print(f"   Response time: {elapsed:.2f}s")
        print(f"   Response preview: {result['response'][:150]}...")
        
        return result['response'], session_id
    except Exception as e:
        print_error(f"Chat request failed: {e}")
        return None, session_id

def get_logs_for_session(session_id, pattern=None):
    """Get Render logs for specific session"""
    try:
        cmd = [
            "render", "logs", 
            "-r", "srv-d44ak76uk2gs73a3psig",
            "--limit", "100",
            "--confirm",
            "-o", "text"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print_warning(f"Render logs command failed: {result.stderr}")
            return []
        
        # Filter logs for this session
        lines = result.stdout.split('\n')
        session_logs = [line for line in lines if session_id in line]
        
        if pattern:
            session_logs = [line for line in session_logs if pattern in line]
        
        return session_logs
    except subprocess.TimeoutExpired:
        print_warning("Render logs command timed out")
        return []
    except Exception as e:
        print_warning(f"Could not fetch logs: {e}")
        return []

def analyze_logs(session_id, test_description):
    """Analyze logs for a specific test session"""
    print(f"\n{Colors.OKBLUE}📊 LOG ANALYSIS: {test_description}{Colors.ENDC}")
    print("-" * 80)
    
    # Wait a moment for logs to propagate
    time.sleep(2)
    
    # Get all logs for this session
    all_logs = get_logs_for_session(session_id)
    
    if not all_logs:
        print_warning("No logs found for this session yet (may take a few seconds)")
        return None, None, None
    
    # Extract key log patterns
    debug_logs = [log for log in all_logs if '[DEBUG]' in log]
    openai_logs = [log for log in all_logs if '[OPENAI]' in log]
    warning_logs = [log for log in all_logs if 'WARNING' in log or '⚠️' in log]
    context_loading = [log for log in all_logs if 'Smart context loading' in log]
    
    # Print context loading decision
    if context_loading:
        print(f"\n{Colors.BOLD}Context Loading Decision:{Colors.ENDC}")
        for log in context_loading:
            print(f"   {log.strip()}")
    
    # Print DEBUG logs (what context_builder loaded)
    if debug_logs:
        print(f"\n{Colors.BOLD}Context Builder Output (DEBUG):{Colors.ENDC}")
        for log in debug_logs[:5]:  # Show first 5 to avoid clutter
            print(f"   {log.strip()}")
    else:
        print_warning("No [DEBUG] logs found - context builder logging may not be working")
    
    # Print OPENAI logs (what OpenAI received)
    if openai_logs:
        print(f"\n{Colors.BOLD}OpenAI Service Input (OPENAI):{Colors.ENDC}")
        for log in openai_logs[:8]:  # Show first 8
            print(f"   {log.strip()}")
    else:
        print_warning("No [OPENAI] logs found - OpenAI service logging may not be working")
    
    # Print warnings
    if warning_logs:
        print(f"\n{Colors.WARNING}Warnings Found:{Colors.ENDC}")
        for log in warning_logs:
            print(f"   {log.strip()}")
    
    # Analysis summary
    print(f"\n{Colors.BOLD}Analysis:{Colors.ENDC}")
    
    # Check if data was loaded
    clients_count = None
    projects_count = None
    permits_count = None
    
    for log in debug_logs:
        if 'Clients count:' in log:
            try:
                clients_count = int(log.split('Clients count:')[1].strip())
            except:
                pass
        if 'Projects count:' in log:
            try:
                projects_count = int(log.split('Projects count:')[1].strip())
            except:
                pass
        if 'Permits count:' in log:
            try:
                permits_count = int(log.split('Permits count:')[1].strip())
            except:
                pass
    
    # Check if OpenAI received data
    openai_has_clients = any('all_clients available: True' in log for log in openai_logs)
    openai_has_projects = any('all_projects available: True' in log for log in openai_logs)
    openai_has_permits = any('all_permits available: True' in log for log in openai_logs)
    
    openai_clients_count = None
    for log in openai_logs:
        if 'all_clients count:' in log:
            try:
                openai_clients_count = int(log.split('all_clients count:')[1].strip())
            except:
                pass
    
    # Report findings
    if clients_count is not None:
        if clients_count > 0:
            print_success(f"Context builder loaded {clients_count} clients")
        else:
            print_error("Context builder loaded 0 clients!")
    else:
        print_warning("Could not determine clients count from DEBUG logs")
    
    if openai_has_clients:
        if openai_clients_count is not None:
            if openai_clients_count > 0:
                print_success(f"OpenAI received {openai_clients_count} clients")
            else:
                print_error("OpenAI received 0 clients!")
        else:
            print_success("OpenAI received all_clients array")
    else:
        print_error("OpenAI did NOT receive all_clients!")
    
    # Check for data loss
    if clients_count is not None and openai_clients_count is not None:
        if clients_count != openai_clients_count:
            print_error(f"DATA LOSS: Context builder had {clients_count} clients but OpenAI got {openai_clients_count}!")
        elif clients_count > 0 and openai_clients_count > 0:
            print_success("No data loss - counts match!")
    
    print("-" * 80)
    
    return clients_count, projects_count, permits_count

def verify_response_accuracy(response, actual_data, test_type):
    """Verify AI response contains accurate data from actual database"""
    print(f"\n{Colors.OKBLUE}🔍 ACCURACY VERIFICATION{Colors.ENDC}")
    print("-" * 80)
    
    issues = []
    
    if test_type == "client_lookup":
        # Check if Javier Martinez details are accurate
        client_name = "Javier Martinez"
        actual_client = None
        for c in actual_data['clients']:
            name = c.get('Full Name') or c.get('Client Name', '')
            if client_name.lower() in name.lower():
                actual_client = c
                break
        
        if actual_client:
            print(f"\n{Colors.BOLD}Expected Data (from Sheets):{Colors.ENDC}")
            print(f"   Name: {actual_client.get('Full Name') or actual_client.get('Client Name')}")
            print(f"   Email: {actual_client.get('Email', 'N/A')}")
            print(f"   Phone: {actual_client.get('Phone', 'N/A')}")
            print(f"   Company: {actual_client.get('Company Name', 'N/A')}")
            print(f"   Role: {actual_client.get('Role', 'N/A')}")
            print(f"   Address: {actual_client.get('Address', 'N/A')}")
            
            # Verify each field in response
            email = actual_client.get('Email', '')
            phone = actual_client.get('Phone', '')
            company = actual_client.get('Company Name', '')
            
            if email and email not in response:
                issues.append(f"Missing email: {email}")
            if phone and phone not in response:
                issues.append(f"Missing phone: {phone}")
            if company and company not in response:
                issues.append(f"Missing company: {company}")
    
    elif test_type == "list_clients":
        # Check if response contains actual client names
        print(f"\n{Colors.BOLD}Expected Data (from Sheets):{Colors.ENDC}")
        print(f"   Total clients: {len(actual_data['clients'])}")
        
        client_names = []
        for c in actual_data['clients']:
            name = c.get('Full Name') or c.get('Client Name', '')
            if name:
                client_names.append(name)
                print(f"   - {name}")
        
        # Check if at least 50% of clients are mentioned
        mentioned = sum(1 for name in client_names if name.lower() in response.lower())
        if mentioned < len(client_names) * 0.5:
            issues.append(f"Only {mentioned}/{len(client_names)} clients mentioned in response")
    
    elif test_type == "qb_customers":
        # Check QB customers list
        print(f"\n{Colors.BOLD}Expected Data (from QuickBooks):{Colors.ENDC}")
        
        # Handle both dict and list responses
        qb_data = actual_data.get('qb_customers', [])
        if isinstance(qb_data, dict):
            customers = qb_data.get('customers', qb_data.get('data', []))
        else:
            customers = qb_data
        
        print(f"   Total QB customers: {len(customers)}")
        
        qb_names = []
        for c in customers[:10]:  # Check first 10
            name = c.get('DisplayName', c.get('display_name', ''))
            if name:
                qb_names.append(name)
                print(f"   - {name}")
        
        # Check if at least some QB customers are mentioned (lenient: at least 1)
        mentioned = sum(1 for name in qb_names if name in response)
        if len(qb_names) > 0 and mentioned == 0:
            issues.append(f"No QB customers mentioned (expected {len(qb_names)})")
    
    elif test_type == "project_query":
        # Check Temple project
        print(f"\n{Colors.BOLD}Expected Data (from Sheets):{Colors.ENDC}")
        temple_project = None
        for p in actual_data['projects']:
            address = p.get('Project Address', '').lower()
            if 'temple' in address:
                temple_project = p
                break
        
        if temple_project:
            print(f"   Address: {temple_project.get('Project Address')}")
            print(f"   Status: {temple_project.get('Status')}")
            print(f"   Client: {temple_project.get('Client Name')}")
            
            # Verify key fields
            if temple_project.get('Status') and temple_project['Status'] not in response:
                issues.append(f"Missing project status: {temple_project['Status']}")
    
    # Print results
    print(f"\n{Colors.BOLD}Verification Result:{Colors.ENDC}")
    if issues:
        for issue in issues:
            print_warning(issue)
        return False
    else:
        print_success("All expected data found in response!")
        return True

def main():
    """Run comprehensive context debug tests"""
    print_section("CONTEXT DEBUG TEST SUITE")
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Purpose: Diagnose smart context handler data loss causing 80% hallucination rate")
    
    # Login
    print("\n🔐 Authenticating...")
    token = login()
    if not token:
        print_error("Cannot proceed without authentication")
        return
    print_success("Authenticated successfully")
    
    # Fetch actual data from API
    actual_data = get_actual_data(token)
    if not actual_data:
        print_error("Cannot proceed without actual data")
        return
    
    # Test cases designed to stress different context loading scenarios
    tests = [
        {
            "num": 1,
            "description": "Client Name Query (should load sheets)",
            "message": "look up javier martinez",
            "session_id": f"test_debug_client_{int(time.time())}",
            "expected_context": "sheets",
            "should_have_clients": True,
            "verify_type": "client_lookup"
        },
        {
            "num": 2,
            "description": "List All Clients (should load sheets)",
            "message": "list all clients from the database",
            "session_id": f"test_debug_list_{int(time.time())}",
            "expected_context": "sheets",
            "should_have_clients": True,
            "verify_type": "list_clients"
        },
        {
            "num": 3,
            "description": "Project Query (should load sheets)",
            "message": "show me the temple project details",
            "session_id": f"test_debug_project_{int(time.time())}",
            "expected_context": "sheets",
            "should_have_clients": True,
            "verify_type": "project_query"
        },
        {
            "num": 4,
            "description": "QuickBooks Query (should load sheets + quickbooks)",
            "message": "list all quickbooks customers",
            "session_id": f"test_debug_qb_{int(time.time())}",
            "expected_context": "sheets, quickbooks",
            "should_have_clients": False,  # QB query doesn't need sheets clients
            "verify_type": "qb_customers"
        },
        {
            "num": 5,
            "description": "Client with QB Request (should load both)",
            "message": "show me javier martinez and his quickbooks invoices",
            "session_id": f"test_debug_both_{int(time.time())}",
            "expected_context": "sheets, quickbooks",
            "should_have_clients": True,
            "verify_type": "client_lookup"
        },
        {
            "num": 6,
            "description": "Generic Greeting (should load none or sheets)",
            "message": "hello",
            "session_id": f"test_debug_hello_{int(time.time())}",
            "expected_context": "none",
            "should_have_clients": False,
            "verify_type": None
        },
        {
            "num": 7,
            "description": "Ambiguous Query (tests default behavior)",
            "message": "what information do you have",
            "session_id": f"test_debug_ambiguous_{int(time.time())}",
            "expected_context": "sheets (default)",
            "should_have_clients": True,
            "verify_type": None
        },
        {
            "num": 8,
            "description": "Create Customer Request (should load sheets + quickbooks)",
            "message": "create a quickbooks customer for javier martinez",
            "session_id": f"test_debug_create_{int(time.time())}",
            "expected_context": "sheets, quickbooks",
            "should_have_clients": True,
            "verify_type": "client_lookup"
        }
    ]
    
    results = []
    
    for test in tests:
        print_section(f"TEST {test['num']}/{len(tests)}: {test['description']}")
        print(f"Expected context: {test['expected_context']}")
        print(f"Should have clients: {'Yes' if test['should_have_clients'] else 'No'}")
        
        response, session_id = test_chat(
            token, 
            test['message'], 
            test['session_id'],
            test['num']
        )
        
        if response:
            # Analyze logs for this test
            clients_count, projects_count, permits_count = analyze_logs(session_id, test['description'])
            
            # Verify counts match actual data
            if clients_count is not None and clients_count != len(actual_data['clients']):
                print_error(f"COUNT MISMATCH: Loaded {clients_count} clients but API has {len(actual_data['clients'])}!")
            
            # Verify response accuracy against actual data
            accuracy_pass = True
            if test['verify_type']:
                accuracy_pass = verify_response_accuracy(response, actual_data, test['verify_type'])
            
            # Check for hallucination indicators
            fake_names = ['John Doe', 'Jane Smith', 'Alex Chang', 'Emily Clark', 'Sarah Johnson', 'Bob Smith', 'Michael Johnson']
            has_fake = any(name in response for name in fake_names)
            
            if has_fake:
                print_error("Response contains FAKE/HALLUCINATED names!")
                accuracy_pass = False
            else:
                print_success("No obvious hallucination detected in response")
            
            results.append({
                'test': test['num'],
                'description': test['description'],
                'session_id': session_id,
                'success': accuracy_pass and not has_fake,
                'accuracy_verified': accuracy_pass
            })
        else:
            results.append({
                'test': test['num'],
                'description': test['description'],
                'session_id': session_id,
                'success': False,
                'accuracy_verified': False
            })
        
        # Wait between tests
        time.sleep(3)
    
    # Final summary
    print_section("TEST SUMMARY")
    
    # Compare actual data counts
    print(f"{Colors.BOLD}Actual Data in System:{Colors.ENDC}")
    print(f"  Clients: {len(actual_data['clients'])}")
    print(f"  Projects: {len(actual_data['projects'])}")
    print(f"  Permits: {len(actual_data['permits'])}")
    print(f"  QB Customers: {len(actual_data['qb_customers'])}")
    print(f"  QB Authenticated: {actual_data['qb_authenticated']}")
    print()
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    accuracy_verified = sum(1 for r in results if r.get('accuracy_verified', False))
    
    print(f"Tests Passed: {passed}/{total} ({(passed/total*100):.1f}%)")
    print(f"Accuracy Verified: {accuracy_verified}/{total}")
    print()
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        accuracy_icon = "✓" if result.get('accuracy_verified') else "?"
        print(f"{status} [{accuracy_icon}] Test {result['test']}: {result['description']}")
        print(f"              Session ID: {result['session_id']}")
    
    print_section("NEXT STEPS")
    
    if passed < total:
        print("❌ Some tests failed - hallucination issue persists")
        print()
        print("Analysis recommendations:")
        print("1. Review DEBUG logs above - are clients being loaded?")
        print("2. Review OPENAI logs above - is data reaching OpenAI?")
        print("3. Look for 'Context has NO clients data!' warnings")
        print("4. Compare counts between DEBUG and OPENAI logs")
        print()
        print("If data is NOT being loaded:")
        print("   → Issue in context_builder.py (smart context too aggressive)")
        print("   → Solution: Implement Step 3 (force load everything)")
        print()
        print("If data IS loaded but NOT reaching OpenAI:")
        print("   → Issue in context merging (chat.py line 83)")
        print("   → Solution: Fix context.update() logic")
        print()
        print("If data reaches OpenAI but AI still hallucinates:")
        print("   → Issue in how OpenAI accesses the data")
        print("   → Solution: Check system prompt and data structure")
    else:
        print_success("All tests passed! Hallucination issue may be resolved")
        print()
        print("Recommended actions:")
        print("1. Run production tests with real user queries")
        print("2. Monitor logs for next 24 hours")
        print("3. If issues persist, collect more specific examples")
    
    print()
    print("Full logs available with:")
    print(f"  render logs -r srv-d44ak76uk2gs73a3psig --limit 200 --confirm -o text")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test suite interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
