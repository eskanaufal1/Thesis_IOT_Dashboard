import React, { useState, useRef, useEffect } from "react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card } from "../components/ui/card";
import { SendIcon } from "../components/Icons";

interface Message {
  sender: "user" | "bot";
  text: string;
}

const ChatbotPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "bot",
      text: "Hello! How can I assist you with your IoT devices today?",
    },
  ]);
  const [userMessage, setUserMessage] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = (): void => {
    if (userMessage.trim() === "") return;

    const newMessages: Message[] = [
      ...messages,
      { sender: "user", text: userMessage },
      {
        sender: "bot",
        text: `Thank you for your message: "${userMessage}". I'm here to help with your IoT device management!`,
      },
    ];

    setMessages(newMessages);
    setUserMessage("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>): void => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          IoT Assistant
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Get help with your IoT devices and system management
        </p>
      </div>

      {/* Chat Container */}
      <Card className="h-[32rem] flex flex-col">
        {/* Messages Area - Scrollable */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.sender === "user"
                    ? "bg-slate-900 text-slate-50 dark:bg-slate-50 dark:text-slate-900"
                    : "bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-50"
                } animate-fade-in`}
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <p className="text-sm">{message.text}</p>
              </div>
            </div>
          ))}
          {/* Invisible element to scroll to */}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area - Fixed at Bottom */}
        <div className="border-t border-slate-200 dark:border-slate-800 p-4">
          <div className="flex space-x-2">
            <Input
              type="text"
              placeholder="Type your message here..."
              value={userMessage}
              onChange={(e) => setUserMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              className="flex-1"
            />
            <Button
              onClick={handleSendMessage}
              variant="default"
              className="flex items-center space-x-2"
            >
              <SendIcon size={16} />
              <span className="hidden sm:inline">Send</span>
            </Button>
          </div>
        </div>
      </Card>

      {/* Quick Actions */}
      <div className="mt-6">
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50 mb-4">
              Quick Actions
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Button
                variant="outline"
                onClick={() => setUserMessage("Show me device status")}
                className="text-left justify-start h-auto p-4"
              >
                <div className="text-left">
                  <div className="flex items-center space-x-2">
                    <span>📊</span>
                    <span>Check Device Status</span>
                  </div>
                </div>
              </Button>
              <Button
                variant="outline"
                onClick={() => setUserMessage("Help with relay control")}
                className="text-left justify-start h-auto p-4"
              >
                <div className="text-left">
                  <div className="flex items-center space-x-2">
                    <span>🔌</span>
                    <span>Relay Control Help</span>
                  </div>
                </div>
              </Button>
              <Button
                variant="outline"
                onClick={() => setUserMessage("Show system statistics")}
                className="text-left justify-start h-auto p-4"
              >
                <div className="text-left">
                  <div className="flex items-center space-x-2">
                    <span>📈</span>
                    <span>System Statistics</span>
                  </div>
                </div>
              </Button>
              <Button
                variant="outline"
                onClick={() => setUserMessage("Troubleshoot offline device")}
                className="text-left justify-start h-auto p-4"
              >
                <div className="text-left">
                  <div className="flex items-center space-x-2">
                    <span>🔧</span>
                    <span>Troubleshooting</span>
                  </div>
                </div>
              </Button>
              <Button
                variant="outline"
                onClick={() => setUserMessage("Add new device")}
                className="text-left justify-start h-auto p-4"
              >
                <div className="text-left">
                  <div className="flex items-center space-x-2">
                    <span>➕</span>
                    <span>Add Device</span>
                  </div>
                </div>
              </Button>
              <Button
                variant="outline"
                onClick={() => setUserMessage("System maintenance tips")}
                className="text-left justify-start h-auto p-4"
              >
                <div className="text-left">
                  <div className="flex items-center space-x-2">
                    <span>🛠️</span>
                    <span>Maintenance Tips</span>
                  </div>
                </div>
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default ChatbotPage;
