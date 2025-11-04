import { Loader2 } from 'lucide-react'

export default function LoadingScreen() {
  return (
    <div className="fixed inset-0 bg-white flex items-center justify-center z-50">
      <div className="text-center">
        <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
        <p className="text-neutral-text font-medium">Loading...</p>
      </div>
    </div>
  )
}
