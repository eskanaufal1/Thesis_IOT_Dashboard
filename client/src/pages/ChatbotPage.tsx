import React, { useState } from "react";
import { Card, Button, Input } from "../components/UI";
import { SendIcon } from "../components/Icons";

interface Message {
  sender: "user" | "bot";
  text: string;
}

const ChatbotPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { sender: "bot", text: "Hello! How can I assist you with your IoT devices today?" },
  ]);
  const [userMessage, setUserMessage] = useState<string>("");

  const handleSendMessage = (): void => {
    if (userMessage.trim() === "") return;

    const newMessages: Message[] = [
      ...messages,
      { sender: "user", text: userMessage },
      { sender: "bot", text: `Thank you for your message: "${userMessage}". I'm here to help with your IoT device management!` },
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
      <Card className="h-96">
        <div className="flex flex-col h-full">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto mb-4 space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.sender === "user"
                      ? "bg-primary-600 text-white"
                      : "bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white"
                  } animate-fade-in`}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <p className="text-sm">{message.text}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Input Area */}
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
        <Card title="Quick Actions">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Button
              variant="secondary"
              onClick={() => setUserMessage("Show me device status")}
              className="text-left justify-start"
            >
              📊 Check Device Status
            </Button>
            <Button
              variant="secondary"
              onClick={() => setUserMessage("Help with relay control")}
              className="text-left justify-start"
            >
              🔌 Relay Control Help
            </Button>
            <Button
              variant="secondary"
              onClick={() => setUserMessage("Show system statistics")}
              className="text-left justify-start"
            >
              📈 System Statistics
            </Button>
            <Button
              variant="secondary"
              onClick={() => setUserMessage("Troubleshoot offline device")}
              className="text-left justify-start"
            >
              🔧 Troubleshooting
            </Button>
            <Button
              variant="secondary"
              onClick={() => setUserMessage("Add new device")}
              className="text-left justify-start"
            >
              ➕ Add Device
            </Button>
            <Button
              variant="secondary"
              onClick={() => setUserMessage("System maintenance tips")}
              className="text-left justify-start"
            >
              🛠️ Maintenance Tips
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default ChatbotPage;


