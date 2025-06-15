import React, { useState } from "react";
import { Input, Button, List, Typography, Space, Flex } from "antd";
import { SendOutlined } from "@ant-design/icons";
import { type ChangeEvent } from "react"; // Type-only import

const { Text, Link } = Typography;

// Define types for the message
interface Message {
  sender: "user" | "bot";
  text: string;
}

const ChatbotPage: React.FC = () => {
  // State to store all messages (keeping full message history)
  const [messages, setMessages] = useState<Message[]>([
    { sender: "bot", text: "Hello! How can I assist you today?" },
  ]);

  // State to store the user's message
  const [userMessage, setUserMessage] = useState<string>("");

  // Function to handle user input
  const handleUserInputChange = (e: ChangeEvent<HTMLInputElement>): void => {
    setUserMessage(e.target.value);
  };

  // Function to handle sending messages
  const handleSendMessage = (): void => {
    if (userMessage.trim() === "") return;

    // Add user message and bot response to the chat history
    const newMessages: Message[] = [
      ...messages,
      { sender: "user", text: userMessage },
      { sender: "bot", text: `You said: ${userMessage}` },
    ];

    // Update state with the new messages (preserving previous messages)
    setMessages(newMessages);

    // Clear input field
    setUserMessage("");
  };

  // Function to handle Enter key press
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>): void => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  };

  return (
    <div style={{ maxWidth: "95%", margin: "0 auto", padding: 20 }}>
      <Typography.Title level={2}>Chatbot</Typography.Title>
      <div
        style={{
          border: "1px solid #ccc",
          borderRadius: 10,
          padding: 10,
          height: "70vh",
          overflowY: "auto",
        }}
      >
        <List
          dataSource={messages}
          renderItem={(message, index) => (
            <List.Item key={index}>
              <Space direction="vertical" style={{ width: "100%" }}>
                <Flex
                  justify={
                    message.sender === "user" ? "flex-end" : "flex-start"
                  }
                  style={{
                    textAlign: message.sender === "user" ? "right" : "left",
                  }}
                >
                  <Space direction="vertical">
                    <Text strong>
                      {message.sender === "user" ? "You" : "Assistant"}
                    </Text>
                    <Text
                      style={{
                        backgroundColor:
                          message.sender === "user" ? "#d1e7dd" : "#f8d7da",
                        borderRadius: 10,
                        padding: "8px 12px",
                      }}
                    >
                      {message.text}
                    </Text>
                  </Space>
                </Flex>
              </Space>
            </List.Item>
          )}
        />
      </div>

      <div
        style={{
          marginTop: 10,
          display: "flex",
          justifyContent: "space-between",
        }}
      >
        <Input
          value={userMessage}
          onChange={handleUserInputChange}
          onKeyDown={handleKeyDown} // Handle Enter key press
          placeholder="Type a message"
          style={{ width: "95%" }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSendMessage}
          style={{ marginLeft: 10 }}
        >
          Send
        </Button>
      </div>
    </div>
  );
};

export default ChatbotPage;
