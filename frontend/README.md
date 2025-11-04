# House Renovators AI Portal - Frontend

**Status:** ✅ Production Ready  
**Last Updated:** November 3, 2025  
**Build:** 257KB (73KB gzipped)

Modern corporate web application built with React 19, featuring a complete UI redesign with AppSheet/Notion-inspired design principles.

## 🚀 Quick Start

### Local Development

1. **Install Dependencies**
```bash
cd house-renovators-pwa
npm install
```

2. **Configure Environment**
```bash
# Development environment is pre-configured
# Edit .env.development if needed
```

3. **Start Development Server**
```bash
npm run dev
```

The app will be available at http://localhost:5173

## 🌐 Production Deployment

### Deploy to Cloudflare Pages

1. **Build the Application**
```bash
npm run build
```

2. **Deploy to Cloudflare Pages**
- Connect your GitHub repository to Cloudflare Pages
- Build command: `npm run build`
- Output directory: `dist`
- Environment variables: `VITE_API_URL=https://house-renovators-ai.onrender.com`

### Manual Deployment

1. **Build for Production**
```bash
npm run build
```

2. **Preview Build Locally**
```bash
npm run preview
```

## 📱 PWA Features

- **Offline Support**: Service worker caches app for offline use
- **Install Prompt**: Users can install the app on their devices
- **Push Notifications**: Ready for future notification features
- **Responsive Design**: Works on desktop, tablet, and mobile
- **App-like Experience**: Full-screen, native-like interface

## 🎨 UI Components

### Core Components
- `Header`: Navigation and status indicator
- `ChatBox`: AI assistant chat interface
- `Dashboard`: Main dashboard with stats and quick actions
- `StatusIndicator`: System health display

### Features
- **Real-time Chat**: AI-powered assistance
- **Responsive Design**: Mobile-first approach
- **Dark/Light Mode**: Ready for theme switching
- **Accessibility**: WCAG compliant components

## 🔧 Configuration

### Environment Variables

| Variable | Description | Development | Production |
|----------|-------------|-------------|------------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` | `https://house-renovators-ai.onrender.com` |
| `VITE_ENV` | Environment | `development` | `production` |
| `VITE_ENABLE_DEBUG` | Debug mode | `true` | `false` |

### API Integration

The app connects to the FastAPI backend for:
- Chat message processing
- Permit data retrieval
- Project management
- System status monitoring

## 🏗️ Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── ChatBox.jsx      # AI chat interface
│   ├── Header.jsx       # App navigation
│   └── StatusIndicator.jsx # System status
├── pages/               # Page components
│   └── Dashboard.jsx    # Main dashboard
├── utils/               # Utility functions
│   └── api.js          # API client
├── App.jsx             # Main app component
├── main.jsx            # App entry point
└── index.css           # Global styles
```

## 🎯 Key Features

### Chat Interface
- Natural language queries
- Real-time responses
- Suggested questions
- Action indicators
- Error handling

### Dashboard
- Project statistics
- Recent permits display
- Quick actions
- System status

### PWA Capabilities
- Installable on devices
- Offline functionality
- Background sync (planned)
- Push notifications (planned)

## 🔒 Security

- Environment-based API configuration
- HTTPS-only in production
- Content Security Policy headers
- XSS protection

## 📊 Performance

- Code splitting with Vite
- Lazy loading components
- Service worker caching
- Optimized bundle size
- Fast refresh in development

## 🧪 Development

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Development Tips

1. **Hot Reload**: Changes are reflected instantly
2. **Console Logs**: Check browser console for API calls
3. **Network Tab**: Monitor API requests and responses
4. **PWA Tools**: Use browser dev tools PWA panel

## 🚀 Deployment Checklist

- [ ] Update `VITE_API_URL` for production
- [ ] Test chat functionality
- [ ] Verify responsive design
- [ ] Check PWA installation
- [ ] Test offline functionality
- [ ] Validate API connectivity

## 📱 Mobile Experience

- **Install Prompt**: Appears after user engagement
- **Full Screen**: Hides browser UI when installed
- **Touch Optimized**: Large touch targets
- **Fast Loading**: Optimized for mobile networks

## 🔄 Future Enhancements

- [ ] Push notifications for permit updates
- [ ] Offline data synchronization
- [ ] Voice commands for chat
- [ ] PDF document viewer
- [ ] Calendar integration
- [ ] Team collaboration features

## 🛠️ Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check `VITE_API_URL` configuration
   - Verify backend is running
   - Check CORS settings

2. **PWA Not Installing**
   - Ensure HTTPS in production
   - Check manifest.json validity
   - Verify service worker registration

3. **Chat Not Working**
   - Check API endpoint health
   - Verify OpenAI integration
   - Check browser console for errors

### Debug Mode

Enable debug mode by setting `VITE_ENABLE_DEBUG=true` to see:
- Detailed API logs
- Component render information
- Performance metrics

## 📞 Support

For technical issues:
- Check browser console for errors
- Verify API connectivity at `/health`
- Review network requests in dev tools
- Test PWA functionality with Lighthouse

## 🌟 Technologies Used

- **React 19**: UI framework
- **Vite**: Build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **Heroicons**: Icon library
- **Axios**: HTTP client
- **Workbox**: Service worker management

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
# Test auto-deploy
