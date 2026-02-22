import { useState, useEffect, useRef } from "react";
import { Timer as TimerIcon, AlertTriangle } from "lucide-react";
import "./Timer.css";

export default function Timer({ seconds, onTimeUp, paused = false }) {
    const [remaining, setRemaining] = useState(seconds);
    const intervalRef = useRef(null);

    useEffect(() => {
        setRemaining(seconds);
    }, [seconds]);

    useEffect(() => {
        if (paused || remaining <= 0) {
            clearInterval(intervalRef.current);
            if (remaining <= 0 && onTimeUp) onTimeUp();
            return;
        }

        intervalRef.current = setInterval(() => {
            setRemaining((prev) => {
                if (prev <= 1) {
                    clearInterval(intervalRef.current);
                    if (onTimeUp) onTimeUp();
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(intervalRef.current);
    }, [paused, remaining <= 0]);

    const minutes = Math.floor(remaining / 60);
    const secs = remaining % 60;
    const progress = seconds > 0 ? (remaining / seconds) * 100 : 0;
    const isUrgent = remaining <= 30;
    const isCritical = remaining <= 10;

    return (
        <div className={`timer-container ${isUrgent ? "urgent" : ""} ${isCritical ? "critical" : ""}`}>
            <div className="timer-display">
                {isCritical && <AlertTriangle size={16} className="timer-warn-icon" />}
                <TimerIcon size={16} />
                <span className="timer-digits">
                    {String(minutes).padStart(2, "0")}:{String(secs).padStart(2, "0")}
                </span>
            </div>
            <div className="timer-bar">
                <div
                    className="timer-bar-fill"
                    style={{ width: `${progress}%` }}
                />
            </div>
        </div>
    );
}
