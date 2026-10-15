import { useState, type FormEvent } from "react";
import { CalendarClock, MapPin, Navigation, Route, Truck } from "lucide-react";
import type { CheckpointInterval, RouteAnalysisRequest } from "../../types/routing";

type Props = { onAnalyze: (values: RouteAnalysisRequest) => void | Promise<void>; loading: boolean };
const inputClass = "w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100";
const labelClass = "mb-1.5 flex items-center gap-2 text-sm font-semibold text-slate-700";

export default function RoutePlanner({ onAnalyze, loading }: Props) {
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [departureTime, setDepartureTime] = useState("");
  const [loadWeight, setLoadWeight] = useState("20000");
  const [checkpointInterval, setCheckpointInterval] = useState<CheckpointInterval>(25);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (loading) return;
    const weight = Number(loadWeight);
    if (!Number.isFinite(weight) || weight < 0) return;
    onAnalyze({
      origin: origin.trim(),
      destination: destination.trim(),
      departure_time: new Date(departureTime).toISOString(),
      load_weight: weight,
      checkpoint_interval: checkpointInterval,
    });
  }

  return (
    <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
      <div><label className={labelClass} htmlFor="origin"><MapPin size={16} />Origin</label>
        <input className={inputClass} id="origin" value={origin} onChange={(e) => setOrigin(e.target.value)} minLength={2} maxLength={255} placeholder="Chicago, IL" required /></div>
      <div><label className={labelClass} htmlFor="destination"><Navigation size={16} />Destination</label>
        <input className={inputClass} id="destination" value={destination} onChange={(e) => setDestination(e.target.value)} minLength={2} maxLength={255} placeholder="Indianapolis, IN" required /></div>
      <div><label className={labelClass} htmlFor="departureTime"><CalendarClock size={16} />Departure Time</label>
        <input className={inputClass} id="departureTime" type="datetime-local" value={departureTime} onChange={(e) => setDepartureTime(e.target.value)} required /></div>
      <div><label className={labelClass} htmlFor="loadWeight"><Truck size={16} />Load Weight (lbs)</label>
        <input className={inputClass} id="loadWeight" type="number" min="0" step="any" value={loadWeight} onChange={(e) => setLoadWeight(e.target.value)} required /></div>
      <div><label className={labelClass} htmlFor="checkpointInterval"><Route size={16} />Weather Checkpoints</label>
        <select className={inputClass} id="checkpointInterval" value={checkpointInterval} onChange={(e) => setCheckpointInterval(Number(e.target.value) as CheckpointInterval)}>
          <option value={10}>Every 10 miles</option><option value={25}>Every 25 miles</option><option value={50}>Every 50 miles</option>
        </select></div>
      <button className="w-full rounded-lg bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60" type="submit" disabled={loading}>
        {loading ? "Analyzing routes…" : "Analyze Routes"}
      </button>
    </form>
  );
}
