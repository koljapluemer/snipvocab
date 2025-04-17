import { useToast } from '@/modules/elements/toast/useToast'

const DAILY_VIDEO_LIMIT = 2
const STORAGE_KEY = 'daily_video_watches'

interface DailyWatches {
    date: string
    count: number
}

export const getDailyWatches = (): DailyWatches => {
    const today = new Date().toISOString().split('T')[0]
    const storedData = localStorage.getItem(STORAGE_KEY)
    let dailyWatches: DailyWatches = storedData ? JSON.parse(storedData) : { date: today, count: 0 }

    // Reset count if it's a new day
    if (dailyWatches.date !== today) {
        dailyWatches = { date: today, count: 0 }
        localStorage.setItem(STORAGE_KEY, JSON.stringify(dailyWatches))
    }

    return dailyWatches
}

export const incrementDailyWatches = (): boolean => {
    const dailyWatches = getDailyWatches()
    dailyWatches.count++
    localStorage.setItem(STORAGE_KEY, JSON.stringify(dailyWatches))
    return dailyWatches.count > DAILY_VIDEO_LIMIT
}

export const useVideoWatchTracking = () => {
    const toast = useToast()
    
    const trackVideoWatch = () => {
        const isLimitReached = incrementDailyWatches()
        if (isLimitReached) {
            toast.warning('You\'ve reached your daily video limit. Upgrade to Premium for unlimited access!')
            return true
        }
        return false
    }

    return {
        trackVideoWatch
    }
}
