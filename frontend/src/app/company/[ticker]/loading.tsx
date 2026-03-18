export default function DashboardLoading() {
  return (
    <div className="fixed inset-0 flex flex-col items-center justify-center gap-5">
      <div className="w-16 h-16 rounded-full border-[5px] border-gray-800 border-t-violet-500 animate-spin" />
      <p className="text-gray-300 text-base animate-pulse">
        Fetching latest market data...
      </p>
    </div>
  );
}
