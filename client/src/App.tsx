import React, { useState } from "react";
import {
  BarChartOutlined,
  PieChartOutlined,
  CodeOutlined,
  DesktopOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from "@ant-design/icons";
import DashboardPage from "./pages/DashboardPage";
import DevicePage from "./pages/DevicePage";
import StatisticPage from "./pages/StatisticPage";
import { Button, Layout, Menu, Avatar, theme, Grid } from "antd";
import Logo from "./assets/unpam.svg";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import ChatbotPage from "./pages/ChatbotPage";
const { useBreakpoint } = Grid;

const App: React.FC = () => {
  const screens = useBreakpoint();
  const [collapsed, setCollapsed] = useState(false);
  const { token } = theme.useToken();
  const { Header, Sider, Content } = Layout;
  return (
    <Router>
      <Layout
        hasSider
        style={{
          margin: 0,
          minHeight: "100vh",
        }}
      >
        <Sider
          trigger={null}
          // collapsible
          // collapsed={
          //   collapsed == true || screens.xs || screens.sm ? true : false
          // }
          style={{ padding: "10px" }}
          breakpoint="sm"
          collapsedWidth="60"
        >
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              marginBottom: "20px",
              marginTop: "10px",
            }}
          >
            <Avatar
              size={70}
              src={Logo}
              style={{
                backgroundColor: "#ffffff",
                display: screens.xs || screens.sm ? "none" : "block",
              }}
            ></Avatar>
          </div>

          <Menu
            theme="dark"
            mode="inline"
            defaultSelectedKeys={["1"]}
            items={[
              {
                key: "1",
                icon: <BarChartOutlined />,
                label: <Link to="/">Dashboard</Link>,
              },
              {
                key: "2",
                icon: <DesktopOutlined />,
                label: <Link to="/device">Devices</Link>,
              },
              {
                key: "3",
                icon: <PieChartOutlined />,
                label: <Link to="/statistic">Statistics</Link>,
              },
              {
                key: "4",
                icon: <CodeOutlined />,
                label: <Link to="/chatbot">Chatbots</Link>,
              },
            ]}
          />
        </Sider>
        <Layout>
          <Header
            style={{
              padding: 0,
              background: token.colorBgContainer,
              border: "1px solid #d9d9d9",
            }}
          >
            {/* <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              style={{
                fontSize: "16px",
                width: 64,
                height: 64,
              }}
            /> */}
            <Button
              type="primary"
              style={{
                marginLeft: 16,
              }}
              onClick={() => alert("Button Clicked!")}
            >
              Click Me
            </Button>
          </Header>
          <Content
            style={{
              border: "1px solid #d9d9d9",
              borderRadius: "8px",
            }}
          >
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/device" element={<DevicePage />} />
              <Route path="/statistic" element={<StatisticPage />} />
              <Route path="/chatbot" element={<ChatbotPage />} />
              <Route path="*" element={<div>Not Found</div>} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Router>
  );
};

export default App;
