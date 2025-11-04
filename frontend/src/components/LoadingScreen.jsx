import { Loader2 } from 'lucide-react'

export default function LoadingScreen() {
  return (
    <div className="fixed inset-0 bg-gradient-to-br from-blue-50 to-slate-50 flex items-center justify-center z-[9999]">
      <div className="text-center">
        <div className="flex justify-center mb-6">
          <Loader2 
            className="w-16 h-16 text-blue-600 animate-spin" 
            strokeWidth={2.5} 
          />
        </div>
        <h2 className="text-2xl font-bold text-slate-800 mb-2">
          House Renovators
        </h2>
        <p className="text-base text-slate-600 font-medium">
          Loading your portal...
        </p>
      </div>
    </div>
  )
}
