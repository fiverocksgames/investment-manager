const capabilities = [
  ['Market', 'Track market regime, momentum, and risk signals.'],
  ['Portfolio', 'Review allocation, concentration, and rebalancing needs.'],
  ['Recommendations', 'Explain ETF candidates with evidence and risks.'],
]

function App() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-950">
      <section className="mx-auto max-w-6xl px-6 py-16 sm:py-24">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">
          Investment Decision Support System
        </p>
        <h1 className="mt-4 max-w-3xl text-4xl font-bold tracking-tight sm:text-6xl">
          Build long-term investment decisions on clear evidence.
        </h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
          Investment Manager is an ETF-first decision-support platform. It does
          not place trades and does not promise returns.
        </p>

        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {capabilities.map(([title, description]) => (
            <article
              className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
              key={title}
            >
              <h2 className="text-xl font-semibold">{title}</h2>
              <p className="mt-3 leading-7 text-slate-600">{description}</p>
            </article>
          ))}
        </div>

        <aside className="mt-12 rounded-2xl bg-slate-900 p-6 text-slate-100">
          <h2 className="font-semibold">Phase 1 status</h2>
          <p className="mt-2 text-slate-300">
            Frontend platform bootstrap in progress. Market data, portfolio
            calculations, authentication, and recommendations are not yet
            connected.
          </p>
        </aside>
      </section>
    </main>
  )
}

export default App
