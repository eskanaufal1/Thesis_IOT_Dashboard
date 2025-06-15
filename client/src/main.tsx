import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { ConfigProvider, theme } from "antd";
import App from "./App.tsx";
import "antd/dist/reset.css"; // Reset Ant Design styles

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ConfigProvider
      theme={{
        // algorithm: theme.darkAlgorithm, // 👈 this enables dark mode
        token: {
          // colorPrimary: "#00b96b",
          borderRadiusLG: 8,
          // colorPrimaryBg: "#000e21",
          // colorBgContainer: "#111a2c", // optional override
        },
      }}
    >
      <App />
    </ConfigProvider>
  </StrictMode>
);
