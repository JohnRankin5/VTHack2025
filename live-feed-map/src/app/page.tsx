export default function Home() {
  return (
    <div className="font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
        <h1 className="text-4xl font-semibold text-center sm:text-left">Firefighter Helmet HUD</h1>

        {/* Placeholder for your live feed and map */}
        <div className="w-full flex flex-col gap-4 sm:flex-row sm:gap-8">
          <div className="w-full sm:w-[48%] bg-gray-300 h-64 rounded-md">
            <h3 className="text-center p-4">Live Feed Placeholder</h3>
            {/* Placeholder for video feed or camera */}
            <div className="w-full h-full bg-gray-500 flex items-center justify-center text-white">
              Camera Feed
            </div>
          </div>
          <div className="w-full sm:w-[48%] bg-gray-300 h-64 rounded-md">
            <h3 className="text-center p-4">Map Placeholder</h3>
            {/* Placeholder for map (you can use Leaflet here) */}
            <div className="w-full h-full bg-gray-700 flex items-center justify-center text-white">
              Map Here
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
