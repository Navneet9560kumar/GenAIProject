import { useState } from "react";
import axios from "axios";

const HITESH_AVATAR = "https://i.imgur.com/0y0y0y0.png"; // Placeholder avatar URL

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const sendMessage = async () => {
    if (input.trim() === "") return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);
    try {
      const res = await axios.post("http://localhost:8000/chat", {
        message: input,
      });
      const botMessage = { role: "bot", content: res.data.reply };
      setMessages((prev) => [...prev, botMessage]);
    } catch {
      const errorMessage = { role: "bot", content: "Error connecting to server." };
      setMessages((prev) => [...prev, errorMessage]);
    }
    setIsTyping(false);
    setInput("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  const handleDeleteChat = () => {
    setMessages([]);
  };

  return (
    <div className="h-screen w-full flex bg-gradient-to-br from-[#23272a] via-[#2c2f36] to-[#23272a]">
      {/* Sidebar */}
      <div className="w-64 bg-[#23272a] flex flex-col items-center py-10 border-r border-[#2f3136]">
        <img src="/Images/download.jpeg" alt="Hitesh Choudhary" className="w-24 h-24 rounded-full border-4 border-[#7289da] shadow-lg mb-4" />
        <div className="text-2xl font-bold text-[#7289da] mb-1">Hitesh Choudhary</div>
        <div className="text-[#99aab5] text-sm mb-2">Online</div>
        <div className="text-[#dcddde] text-center text-xs px-4">Your coding mentor and AI friend!</div>
      </div>
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full">
        {/* Header */}
        <div className="h-16 flex items-center px-8 bg-[#2f3136] border-b border-[#23272a] shadow text-xl font-semibold text-[#7289da] tracking-wide justify-between">
          <span>💬 Chat with Hitesh Choudhary</span>
          <button
            onClick={handleDeleteChat}
            className="ml-4 px-4 py-2 bg-gradient-to-br from-red-500 to-pink-600 text-white rounded-lg font-semibold shadow hover:scale-105 hover:from-red-600 hover:to-pink-700 transition-all duration-200 text-base"
          >
            Delete Chat
          </button>
        </div>
        {/* Chat Messages */}
        <div className="flex-1 w-full flex flex-col items-center justify-end">
          <div className="w-full max-w-2xl flex-1 overflow-y-auto px-6 py-8" style={{ minHeight: '400px' }}>
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`mb-5 flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "bot" && (
                  <img src="/Images/download.jpeg" alt="Hitesh" className="w-10 h-10 rounded-full mr-3 self-end shadow-md border-2 border-[#7289da]" />
                )}
                <div
                  className={`px-5 py-3 rounded-2xl max-w-md text-lg shadow-md animate-fade-in font-medium flex flex-col ${
                    msg.role === "user"
                      ? "bg-gradient-to-br from-[#5865f2] to-[#7289da] text-white rounded-br-3xl rounded-tr-2xl"
                      : "bg-[#36393f] text-[#dcddde] border border-[#23272a] rounded-bl-3xl rounded-tl-2xl"
                  }`}
                  style={{ wordBreak: 'break-word' }}
                >
                  {msg.role === "bot" && (
                    <span className="text-xs text-[#7289da] font-bold mb-1">Hitesh Choudhary</span>
                  )}
                  {msg.content}
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="mb-5 flex justify-start">
                <img src="/Images/download.jpeg" alt="Hitesh" className="w-10 h-10 rounded-full mr-3 self-end shadow-md border-2 border-[#7289da]" />
                <div className="px-5 py-3 rounded-2xl max-w-md text-lg bg-[#36393f] text-[#dcddde] border border-[#23272a] flex items-center gap-2 animate-fade-in">
                  <span className="typing-dot bg-[#7289da] rounded-full w-2 h-2 inline-block animate-bounce mr-1"></span>
                  <span className="typing-dot bg-[#7289da] rounded-full w-2 h-2 inline-block animate-bounce delay-150 mr-1"></span>
                  <span className="typing-dot bg-[#7289da] rounded-full w-2 h-2 inline-block animate-bounce delay-300"></span>
                  <span className="ml-2 text-sm text-[#99aab5]">Hitesh is typing...</span>
                </div>
              </div>
            )}
          </div>
          {/* Input Area */}
          <div className="w-full max-w-2xl flex mb-8 px-6">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              className="flex-1 p-3 border-none rounded-l-2xl focus:outline-none bg-[#40444b] text-[#dcddde] shadow-inner text-lg placeholder-[#99aab5]"
            />
            <button
              onClick={sendMessage}
              className="bg-gradient-to-br from-[#5865f2] to-[#7289da] text-white px-6 py-3 rounded-r-2xl font-semibold shadow-lg hover:scale-105 hover:from-[#4752c4] hover:to-[#5865f2] transition-all duration-200"
            >
              Send
            </button>
          </div>
        </div>
        <style>{`
          .animate-fade-in {
            animation: fadeIn 0.5s;
          }
          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
          }
          .typing-dot {
            animation: bounce 1s infinite alternate;
          }
          .typing-dot.delay-150 {
            animation-delay: 0.15s;
          }
          .typing-dot.delay-300 {
            animation-delay: 0.3s;
          }
          @keyframes bounce {
            0% { transform: translateY(0); }
            100% { transform: translateY(-6px); }
          }
        `}</style>
      </div>
    </div>
  );
}
