import React from 'react';

function Landing({ onLoginClick }) {
  return (
    <div className="bg-[#050914] text-white font-body-md selection:bg-secondary selection:text-white min-h-screen overflow-hidden relative">
      
      {/* Background Ambience */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-[#00e3fd]/10 blur-[150px] rounded-full mix-blend-screen animate-pulse"></div>
        <div className="absolute top-[40%] right-[-10%] w-[30%] h-[50%] bg-[#9466ff]/10 blur-[150px] rounded-full mix-blend-screen"></div>
        <div className="absolute bottom-[-10%] left-[20%] w-[50%] h-[40%] bg-secondary/10 blur-[120px] rounded-full mix-blend-screen"></div>
        {/* Grid Pattern overlay */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAwIDQwIEwgNDAgNDAgNDAgMCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMDMpIiBzdHJva2Utd2lkdGg9IjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-50"></div>
      </div>

      {/* Top Navigation Bar */}
      <nav className="fixed top-0 w-full z-50 bg-[#050914]/60 backdrop-blur-xl border-b border-white/5">
        <div className="flex justify-between items-center px-6 md:px-12 py-4 max-w-[1600px] mx-auto">
          <div className="font-headline-md text-2xl font-bold tracking-tight text-white flex items-center gap-2">
             <span className="material-symbols-outlined text-secondary">hub</span>
             SemanticEdge <span className="text-secondary font-light">5G</span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a className="text-white/70 hover:text-white transition-colors duration-300 font-label-caps text-[12px] tracking-widest" href="#architecture">Architecture</a>
            <a className="text-white/70 hover:text-white transition-colors duration-300 font-label-caps text-[12px] tracking-widest" href="#pipeline">Pipeline</a>
            <a className="text-white/70 hover:text-white transition-colors duration-300 font-label-caps text-[12px] tracking-widest" href="#interface">NLQ Interface</a>
            <a className="text-white/70 hover:text-white transition-colors duration-300 font-label-caps text-[12px] tracking-widest" href="#specs">Specs</a>
          </div>
          <button onClick={onLoginClick} className="bg-white/10 border border-white/20 text-white px-6 py-2 rounded-full font-label-caps text-[12px] tracking-widest hover:bg-white hover:text-black transition-all duration-300 cursor-pointer flex items-center gap-2">
            Operator Login <span className="material-symbols-outlined text-[14px]">login</span>
          </button>
        </div>
      </nav>

      <main className="pt-32 relative z-10 max-w-[1600px] mx-auto px-6 md:px-12">
        
        {/* Hero Section */}
        <section className="relative min-h-[85vh] flex items-center">
          <div className="grid lg:grid-cols-2 items-center gap-16">
            <div className="text-left relative">
              <div className="inline-block border border-secondary/30 bg-secondary/10 px-4 py-1 rounded-full mb-6">
                <span className="font-label-caps text-[10px] text-secondary tracking-[0.2em]">REDEFINING EDGE ANALYTICS</span>
              </div>
              <h1 className="font-display-lg text-5xl md:text-7xl mb-8 leading-[1.1] font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-white/40">
                Deploy Intelligence to Video, Not Video to Intelligence.
              </h1>
              <p className="font-body-lg text-lg text-white/60 mb-10 max-w-xl leading-relaxed">
                Surveillance today is a paradox at scale. We eliminate bandwidth bottlenecks and privacy liabilities by running real-time YOLOv8 inference locally, shrinking 8 Mbps HD video into 2 KB/s of structured semantic metadata transmitted over 5G.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <button onClick={onLoginClick} className="bg-gradient-to-r from-[#00e3fd] to-[#006875] text-black font-bold rounded-full px-8 py-4 font-label-caps text-[12px] tracking-widest hover:shadow-[0_0_30px_rgba(0,227,253,0.4)] transition-all flex items-center justify-center gap-2 cursor-pointer">
                  ACCESS LIVE TERMINAL <span className="material-symbols-outlined">arrow_forward</span>
                </button>
                <button className="border border-white/20 bg-white/5 rounded-full px-8 py-4 font-label-caps text-[12px] tracking-widest hover:bg-white/10 transition-all text-white backdrop-blur-md">
                  READ THE WHITEPAPER
                </button>
              </div>
            </div>
            
            {/* Abstract Floating Graphic */}
            <div className="relative flex justify-center items-center h-[500px] perspective-1000 hidden lg:flex">
               <div className="absolute w-[400px] h-[400px] border border-white/10 rounded-full animate-[spin_20s_linear_infinite]"></div>
               <div className="absolute w-[300px] h-[300px] border border-secondary/30 rounded-full animate-[spin_15s_linear_reverse_infinite] border-dashed"></div>
               
               {/* Core Node */}
               <div className="relative z-10 w-48 h-48 bg-gradient-to-br from-[#131b2e] to-[#001f24] rounded-3xl border border-secondary shadow-[0_0_50px_rgba(0,227,253,0.2)] flex items-center justify-center flex-col animate-[bounce_4s_ease-in-out_infinite]">
                 <span className="material-symbols-outlined text-6xl text-secondary mb-2">memory</span>
                 <span className="font-label-caps text-[10px] tracking-widest text-[#00e3fd]">YOLOv8-NANO EDGE</span>
               </div>
               
               {/* Floating Badges */}
               <div className="absolute top-20 right-10 bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-3 flex items-center gap-2 animate-[bounce_5s_ease-in-out_infinite_0.5s]">
                 <span className="material-symbols-outlined text-[#00ff88]">verified_user</span>
                 <div className="text-left">
                   <div className="text-[8px] font-label-caps text-white/50">PRIVACY</div>
                   <div className="text-[12px] font-bold text-white">100% On-Premise</div>
                 </div>
               </div>

               <div className="absolute bottom-20 left-10 bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-3 flex items-center gap-2 animate-[bounce_4.5s_ease-in-out_infinite_1s]">
                 <span className="material-symbols-outlined text-[#9466ff]">5g</span>
                 <div className="text-left">
                   <div className="text-[8px] font-label-caps text-white/50">PAYLOAD REDUCTION</div>
                   <div className="text-[12px] font-bold text-white">&gt;99.9% Compressed</div>
                 </div>
               </div>
            </div>
          </div>
        </section>

        {/* The Problem vs Solution (Bento) */}
        <section id="architecture" className="py-24">
           <div className="text-center mb-16">
              <h2 className="font-headline-md text-3xl md:text-4xl mb-4 font-bold">The Surveillance Paradox</h2>
              <p className="text-white/50 max-w-2xl mx-auto">The industry is forced to choose between blind storage or privacy-violating exposed streaming. SemanticEdge introduces the third option.</p>
           </div>
           
           <div className="grid md:grid-cols-3 gap-6">
              {/* Problem 1 */}
              <div className="bg-white/5 border border-error/20 rounded-3xl p-8 backdrop-blur-sm hover:border-error/50 transition-colors">
                <span className="material-symbols-outlined text-4xl text-error mb-6">dns</span>
                <h3 className="font-headline-md text-xl mb-3 font-bold">Blind Local Storage</h3>
                <p className="text-white/60 text-sm leading-relaxed mb-6">
                  High maintenance hardware on-site. Footage sits unindexed and unsearchable. Finding an incident requires exhausting manual review.
                </p>
                <div className="text-error font-label-caps text-[10px] tracking-widest flex items-center gap-2">
                  <span className="material-symbols-outlined text-[14px]">close</span> OPERATIONALLY INERT
                </div>
              </div>
              
              {/* Problem 2 */}
              <div className="bg-white/5 border border-error/20 rounded-3xl p-8 backdrop-blur-sm hover:border-error/50 transition-colors">
                <span className="material-symbols-outlined text-4xl text-error mb-6">cloud_upload</span>
                <h3 className="font-headline-md text-xl mb-3 font-bold">Exposed Cloud Streaming</h3>
                <p className="text-white/60 text-sm leading-relaxed mb-6">
                  Streaming 1080p consumes 2-8 Mbps continuously. Scalability collapses. Every pixel leaving the premises becomes an instant privacy liability.
                </p>
                <div className="text-error font-label-caps text-[10px] tracking-widest flex items-center gap-2">
                  <span className="material-symbols-outlined text-[14px]">close</span> BANDWIDTH PROHIBITIVE
                </div>
              </div>

              {/* Solution */}
              <div className="bg-gradient-to-br from-[#131b2e] to-[#001f24] border border-secondary rounded-3xl p-8 shadow-[0_0_30px_rgba(0,227,253,0.1)] relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-32 h-32 bg-secondary/20 blur-3xl rounded-full group-hover:bg-secondary/40 transition-colors"></div>
                <div className="absolute top-4 right-4 bg-secondary/20 text-secondary border border-secondary/30 px-3 py-1 rounded-full font-label-caps text-[8px] tracking-widest">
                  THE 3RD OPTION
                </div>
                <span className="material-symbols-outlined text-4xl text-[#00e3fd] mb-6 relative z-10">hub</span>
                <h3 className="font-headline-md text-xl mb-3 font-bold relative z-10 text-white">5G-Native Architecture</h3>
                <p className="text-white/60 text-sm leading-relaxed mb-6 relative z-10">
                  Analyze locally via an INT8-optimized YOLOv8 pipeline. Extract multi-class objects and spatial tags. Send only a ~500 byte JSON payload over 5G NR.
                </p>
                <div className="text-[#00ff88] font-label-caps text-[10px] tracking-widest flex items-center gap-2 relative z-10">
                  <span className="material-symbols-outlined text-[14px]">check</span> PRIVACY BY DESIGN
                </div>
              </div>
           </div>
        </section>

        {/* Intelligence Pipeline Flow */}
        <section id="pipeline" className="py-24 border-t border-white/5">
          <div className="grid lg:grid-cols-2 items-center gap-16">
            <div>
              <div className="inline-block border border-[#9466ff]/30 bg-[#9466ff]/10 px-4 py-1 rounded-full mb-6">
                <span className="font-label-caps text-[10px] text-[#9466ff] tracking-[0.2em]">DUAL-STORE PIPELINE</span>
              </div>
              <h2 className="font-headline-md text-3xl md:text-4xl mb-6 font-bold">Ingestion & Embedding Flow</h2>
              <p className="text-white/60 text-md leading-relaxed mb-6">
                Structured metadata events are written to <strong className="text-white">MongoDB Atlas</strong> time-series collections for fast exact-match lookups. Simultaneously, semantic content is embedded into high-dimensional vectors and stored in <strong className="text-white">Pinecone</strong>.
              </p>
              <p className="text-white/60 text-md leading-relaxed mb-8">
                This dual architecture unlocks orthogonal queries: exact spatial/temporal lookup and fuzzy semantic similarity search, all monitored by a real-time Node.js alert engine with sub-second response.
              </p>
              
              <ul className="space-y-4">
                <li className="flex items-start gap-4">
                  <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center shrink-0 border border-white/20">
                    <span className="material-symbols-outlined text-[16px] text-white">videocam</span>
                  </div>
                  <div>
                    <h4 className="font-bold text-sm">Ephemeral Frame Retrieval</h4>
                    <p className="text-xs text-white/50 mt-1">Raw video stays on-prem in a 72-hr circular buffer. Retrieved securely via WebSocket only upon authorized flag.</p>
                  </div>
                </li>
                <li className="flex items-start gap-4">
                  <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center shrink-0 border border-white/20">
                    <span className="material-symbols-outlined text-[16px] text-white">cell_tower</span>
                  </div>
                  <div>
                    <h4 className="font-bold text-sm">MEC Offloading</h4>
                    <p className="text-xs text-white/50 mt-1">MQTT over TLS 1.3 straight to the 5G base station MEC, bypassing consumer traffic via network slicing.</p>
                  </div>
                </li>
              </ul>
            </div>
            
            {/* Abstract Pipeline Graphic */}
            <div className="bg-[#0b101e] border border-white/10 rounded-3xl p-8 relative shadow-2xl flex flex-col gap-6">
              <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[#131b2e]/50 rounded-3xl pointer-events-none"></div>
              
              <div className="flex items-center gap-4 relative z-10">
                <div className="w-12 h-12 bg-white/5 border border-white/20 rounded-xl flex items-center justify-center shrink-0">
                  <span className="material-symbols-outlined text-white">camera</span>
                </div>
                <div className="h-[1px] flex-1 bg-gradient-to-r from-white/20 to-secondary/50 relative overflow-hidden">
                  <div className="absolute top-0 left-0 h-full w-1/3 bg-gradient-to-r from-transparent via-secondary to-transparent animate-[translateX_2s_linear_infinite]"></div>
                </div>
                <div className="w-24 bg-secondary/10 border border-secondary text-secondary font-label-caps text-[8px] text-center py-2 rounded-lg">
                  8 MBPS RAW
                </div>
              </div>

              <div className="bg-gradient-to-r from-[#131b2e] to-secondary/20 border border-secondary/50 rounded-xl p-4 flex items-center justify-between relative z-10">
                <div className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-secondary">memory</span>
                  <div>
                    <div className="text-sm font-bold text-white">Edge Node</div>
                    <div className="text-[10px] font-label-caps text-white/50">YOLOv8 INT8 INFERENCE</div>
                  </div>
                </div>
                <span className="material-symbols-outlined text-[#00ff88]">filter_alt</span>
              </div>

              <div className="flex items-center gap-4 relative z-10">
                <div className="w-12 h-12 bg-[#9466ff]/10 border border-[#9466ff]/50 rounded-xl flex items-center justify-center shrink-0 text-[#9466ff]">
                  <span className="material-symbols-outlined">5g</span>
                </div>
                <div className="h-[1px] flex-1 bg-gradient-to-r from-[#9466ff]/50 to-white/20 relative overflow-hidden">
                  <div className="absolute top-0 left-0 h-full w-1/3 bg-gradient-to-r from-transparent via-[#9466ff] to-transparent animate-[translateX_2s_linear_infinite_0.5s]"></div>
                </div>
                <div className="w-24 bg-[#9466ff]/10 border border-[#9466ff] text-[#9466ff] font-label-caps text-[8px] text-center py-2 rounded-lg">
                  2 KB/S JSON
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 relative z-10">
                <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
                  <span className="material-symbols-outlined text-white/50 mb-2">database</span>
                  <div className="text-[10px] font-label-caps text-white">MongoDB Atlas</div>
                  <div className="text-[8px] text-white/40 mt-1">TIME-SERIES DATA</div>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
                  <span className="material-symbols-outlined text-white/50 mb-2">view_in_ar</span>
                  <div className="text-[10px] font-label-caps text-white">Pinecone</div>
                  <div className="text-[8px] text-white/40 mt-1">VECTOR EMBEDDINGS</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Telegram NLQ Interface */}
        <section id="interface" className="py-24 border-t border-white/5">
           <div className="grid lg:grid-cols-2 gap-16 items-center">
              {/* Telegram Mockup */}
              <div className="bg-[#131b2e] rounded-3xl p-6 md:p-8 border border-white/10 flex flex-col shadow-2xl relative overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-br from-transparent to-[#24A1DE]/10 pointer-events-none group-hover:to-[#24A1DE]/20 transition-all"></div>
                
                <div className="flex items-center gap-3 mb-8 relative z-10 border-b border-white/10 pb-4">
                  <div className="w-10 h-10 rounded-full bg-[#24A1DE] flex items-center justify-center text-white shrink-0 shadow-[0_0_15px_rgba(36,161,222,0.4)]">
                    <span className="material-symbols-outlined text-xl">send</span>
                  </div>
                  <div>
                    <div className="font-bold text-white text-sm">Telegram NLQ Operator</div>
                    <div className="text-[10px] text-[#24A1DE] font-label-caps tracking-widest">BOT</div>
                  </div>
                </div>
                
                <div className="flex-1 flex flex-col font-body-md overflow-hidden relative z-10 space-y-6">
                  {/* User Message */}
                  <div className="bg-white/10 border border-white/10 p-4 rounded-2xl rounded-tr-none max-w-[85%] self-end text-white backdrop-blur-sm relative">
                    "Find every instance of a black motorcycle near Gate 2 this week."
                    <div className="text-[10px] text-white/40 text-right mt-2 font-label-caps">11:42 AM</div>
                  </div>
                  
                  {/* Bot Processing */}
                  <div className="self-start flex gap-2 items-center">
                     <div className="w-6 h-6 rounded-full bg-[#24A1DE] flex items-center justify-center"><span className="material-symbols-outlined text-[12px] text-white">smart_toy</span></div>
                     <div className="flex gap-1 bg-white/5 px-3 py-2 rounded-full border border-white/10">
                       <span className="w-1.5 h-1.5 bg-white/50 rounded-full animate-bounce"></span>
                       <span className="w-1.5 h-1.5 bg-white/50 rounded-full animate-bounce delay-75"></span>
                       <span className="w-1.5 h-1.5 bg-white/50 rounded-full animate-bounce delay-150"></span>
                     </div>
                  </div>

                  {/* Bot Response */}
                  <div className="bg-gradient-to-r from-secondary/20 to-transparent border border-secondary/30 p-4 rounded-2xl rounded-tl-none max-w-[85%] self-start text-white backdrop-blur-sm relative shadow-[inset_2px_0_0_#00e3fd]">
                    <div className="flex items-center gap-2 mb-3 border-b border-white/10 pb-2">
                      <span className="material-symbols-outlined text-sm text-[#00ff88]">check_circle</span>
                      <span className="text-[9px] font-label-caps text-[#00e3fd] tracking-widest">LANGCHAIN HYBRID QUERY EXECUTED</span>
                    </div>
                    <p className="text-sm leading-relaxed mb-3">Found 2 matching events with &gt;90% semantic similarity:</p>
                    
                    <div className="space-y-2">
                      <div className="bg-black/30 rounded-lg p-2 text-xs border border-white/5 flex justify-between items-center">
                        <span className="text-white/70">Oct 24, 14:32 • <span className="text-white">Gate 2</span></span>
                        <span className="bg-[#9466ff]/20 text-[#9466ff] px-2 py-0.5 rounded text-[10px]">96% Match</span>
                      </div>
                      <div className="bg-black/30 rounded-lg p-2 text-xs border border-white/5 flex justify-between items-center">
                        <span className="text-white/70">Oct 25, 09:15 • <span className="text-white">Gate 2</span></span>
                        <span className="bg-[#9466ff]/20 text-[#9466ff] px-2 py-0.5 rounded text-[10px]">91% Match</span>
                      </div>
                    </div>
                    
                    <div className="mt-3 text-[10px] text-white/40 italic">Reply /fetch [id] to establish secure WebSocket tunnel for visual verification.</div>
                  </div>
                </div>

                <div className="mt-8 pt-4 border-t border-white/10 relative z-10 flex gap-2">
                  <div className="flex-1 bg-white/5 border border-white/10 rounded-full px-4 py-3 text-sm text-white/30 flex items-center">
                    Message SemanticEdgeBot...
                  </div>
                  <div className="w-12 h-12 bg-white/5 border border-white/10 rounded-full flex items-center justify-center text-white/50 cursor-not-allowed hover:bg-white/10 transition-colors">
                    <span className="material-symbols-outlined">mic</span>
                  </div>
                </div>
              </div>

              {/* Text Description */}
              <div>
                <div className="inline-block border border-[#24A1DE]/30 bg-[#24A1DE]/10 px-4 py-1 rounded-full mb-6">
                  <span className="font-label-caps text-[10px] text-[#24A1DE] tracking-[0.2em]">OPERATOR EXPERIENCE</span>
                </div>
                <h2 className="font-headline-md text-3xl md:text-4xl mb-6 font-bold">Natural Language as the Interface</h2>
                <p className="text-white/60 text-md leading-relaxed mb-6">
                  No complex dashboard training required for ground operators. The primary interface is a Telegram Bot functioning as a powerful natural language query engine.
                </p>
                <p className="text-white/60 text-md leading-relaxed mb-6">
                  The system translates plain-text intent into structured database queries or vector similarity searches via <strong className="text-white">LangChain</strong>, returning ranked timestamps, camera IDs, and confidence scores within seconds.
                </p>
                <ul className="grid grid-cols-1 gap-4">
                  <li className="bg-white/5 border border-white/10 p-4 rounded-xl flex items-center gap-4">
                    <span className="material-symbols-outlined text-[#00ff88]">flash_on</span>
                    <span className="text-sm font-medium">Sub-second Alerting</span>
                  </li>
                  <li className="bg-white/5 border border-white/10 p-4 rounded-xl flex items-center gap-4">
                    <span className="material-symbols-outlined text-secondary">encrypted</span>
                    <span className="text-sm font-medium">Zero App Installation, Works on any Smartphone</span>
                  </li>
                </ul>
              </div>
           </div>
        </section>

        {/* Specifications & Market Grid */}
        <section id="specs" className="py-24 border-t border-white/5">
          <div className="text-center mb-16">
            <h2 className="font-headline-md text-3xl md:text-4xl mb-4 font-bold">Technical Specifications</h2>
            <p className="text-white/50 max-w-2xl mx-auto">Built from the ground up for 5G Advanced capabilities.</p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="col-span-2 md:col-span-2 bg-[#131b2e] border border-white/10 p-8 rounded-3xl group hover:bg-[#131b2e]/80 transition-colors">
              <span className="font-label-caps text-[10px] text-[#9466ff] tracking-widest mb-2 block">INFERENCE ENGINE</span>
              <h3 className="text-xl font-bold mb-2">YOLOv8-nano</h3>
              <p className="text-sm text-white/50">INT8 quantized · MobileNetV3 · TFLite runtime. Highly optimized for 10-15W power envelopes.</p>
            </div>
            
            <div className="bg-white/5 border border-white/10 p-8 rounded-3xl hover:bg-white/10 transition-colors">
              <span className="font-label-caps text-[10px] text-secondary tracking-widest mb-2 block">EDGE HARDWARE</span>
              <h3 className="text-xl font-bold mb-2">&lt; ₹50K Total</h3>
              <p className="text-sm text-white/50">Jetson Nano or Orange Pi 5 NPU setups.</p>
            </div>
            
            <div className="bg-white/5 border border-white/10 p-8 rounded-3xl hover:bg-white/10 transition-colors">
              <span className="font-label-caps text-[10px] text-[#00e3fd] tracking-widest mb-2 block">TRANSPORT</span>
              <h3 className="text-xl font-bold mb-2">MQTT TLS 1.3</h3>
              <p className="text-sm text-white/50">5G NR Sub-6 GHz · &lt;10 ms E2E latency.</p>
            </div>
            
            <div className="bg-white/5 border border-white/10 p-8 rounded-3xl hover:bg-white/10 transition-colors">
              <span className="font-label-caps text-[10px] text-[#00ff88] tracking-widest mb-2 block">PRIVACY MODEL</span>
              <h3 className="text-xl font-bold mb-2">Zero Raw Video</h3>
              <p className="text-sm text-white/50">GDPR Art. 25 compliant.</p>
            </div>
            
            <div className="bg-white/5 border border-white/10 p-8 rounded-3xl hover:bg-white/10 transition-colors">
              <span className="font-label-caps text-[10px] text-[#24A1DE] tracking-widest mb-2 block">5G DEPENDENCY</span>
              <h3 className="text-xl font-bold mb-2">MEC Offload</h3>
              <p className="text-sm text-white/50">Network slicing & NR-Light for IoT.</p>
            </div>
            
            <div className="col-span-2 md:col-span-2 bg-gradient-to-r from-secondary/10 to-transparent border border-secondary/30 p-8 rounded-3xl relative overflow-hidden">
               <div className="absolute right-0 top-0 h-full w-1/2 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCI+PHBhdGggZD0iTTEwIDBMIDEwIDIwIE0wIDEwIEwgMjAgMTAiIHN0cm9rZT0icmdiYSgwLCAyMjcsIDI1MywgMC4xKSIgZmlsbD0ibm9uZSIvPjwvc3ZnPg==')] opacity-50"></div>
               <span className="font-label-caps text-[10px] text-[#00e3fd] tracking-widest mb-2 block relative z-10">ADDRESSABLE MARKET</span>
               <h3 className="text-2xl font-bold mb-2 text-white relative z-10">63M Small & Medium Businesses</h3>
               <p className="text-sm text-white/60 max-w-sm relative z-10">
                 Achieve payback in under 3 months. Zero recurring cloud video storage fees, zero bandwidth overage, zero camera-licensing.
               </p>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-32 relative text-center border-t border-white/5">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-2xl h-[1px] bg-gradient-to-r from-transparent via-secondary to-transparent"></div>
          
          <h2 className="font-display-lg text-4xl md:text-5xl mb-6 font-bold">Fortify your 5G Edge Infrastructure.</h2>
          <p className="text-white/50 mb-10 max-w-xl mx-auto">
            SemanticEdge doesn't ask your infrastructure to become smarter. It makes it smarter—silently, at the edge, without replacing a single camera.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
             <button onClick={onLoginClick} className="bg-white text-black font-bold rounded-full px-10 py-4 font-label-caps text-[12px] tracking-widest hover:scale-105 transition-all">
                ACCESS PORTAL
             </button>
             <button className="border border-white/20 bg-transparent rounded-full px-10 py-4 font-label-caps text-[12px] tracking-widest hover:bg-white/5 transition-all text-white">
                CONTACT SALES
             </button>
          </div>
        </section>
        
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 bg-[#050914] py-8 relative z-10">
        <div className="max-w-[1600px] mx-auto px-6 md:px-12 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-white/30 text-lg">hub</span>
            <span className="font-bold text-white/50 text-sm">SemanticEdge 5G</span>
          </div>
          <div className="text-white/30 text-xs text-center md:text-right font-label-caps tracking-widest">
            © 2026 SEMANTICEDGE SYSTEMS. POWERED BY 5G ARCHITECTURE.
          </div>
        </div>
      </footer>
      
      <style>{`
        @keyframes translateX {
          from { transform: translateX(-100%); }
          to { transform: translateX(300%); }
        }
      `}</style>
    </div>
  );
}

export default Landing;
