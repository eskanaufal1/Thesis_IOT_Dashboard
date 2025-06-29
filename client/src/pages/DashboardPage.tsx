import React, { useEffect, useState } from "react";
import {
  ApiOutlined,
  WifiOutlined,
  ExclamationCircleOutlined,
  DisconnectOutlined,
} from "@ant-design/icons";
import { Col, Row, Statistic, Layout, Typography, Table } from "antd";
import apiClient from "../api"; // Import your Axios instance

const { Content } = Layout;
const { Title } = Typography;

const DashboardPage = () => {
  // Dummy data for device stats
  const totalDevices = 5;
  const onlineDevices = 4;
  const offlineDevices = 1;
  const maintenanceDevices = 0;

  // State to store relay data from API
  const [relayData, setRelayData] = useState([]);

  useEffect(() => {
    // Fetch device data from the API when the component mounts
    apiClient
      .get("/devices") // API call to fetch device data
      .then((response) => {
        // Assuming response.data is the array of devices you want
        setRelayData(response.data);
      })
      .catch((error) => {
        console.error("Error fetching device data:", error);
      });
  }, []);

  const columns = [
    {
      title: "Device ID",
      dataIndex: "deviceName", // Use the key as the device identifier
      key: "deviceName",
    },
    {
      title: "Status", // Added Status column
      dataIndex: "status", // Assuming 'status' is a field in the data
      key: "status",
      render: (text: string) => (
        <span>
          {text === "Online" ? (
            <WifiOutlined style={{ color: "green", marginRight: 8 }} />
          ) : (
            <DisconnectOutlined style={{ color: "red", marginRight: 8 }} />
          )}
          {text}
        </span>
      ),
    },
    {
      title: "Location", // Added Location column
      dataIndex: "location", // Assuming 'location' is a field in the data
      key: "location",
    },
    {
      title: "Relay 1",
      dataIndex: "relay1", // Relay 1 status
      key: "relay1",
      render: (text: string) => (
        <span style={{ color: text === "On" ? "blue" : "red" }}>{text}</span>
      ),
    },
    {
      title: "Relay 2",
      dataIndex: "relay2", // Relay 2 status
      key: "relay2",
      render: (text: string) => (
        <span style={{ color: text === "On" ? "blue" : "red" }}>{text}</span>
      ),
    },
    {
      title: "Relay 3",
      dataIndex: "relay3", // Relay 3 status
      key: "relay3",
      render: (text: string) => (
        <span style={{ color: text === "On" ? "blue" : "red" }}>{text}</span>
      ),
    },
    {
      title: "Relay 4",
      dataIndex: "relay4", // Relay 4 status
      key: "relay4",
      render: (text: string) => (
        <span style={{ color: text === "On" ? "blue" : "red" }}>{text}</span>
      ),
    },
    {
      title: "Last Seen",
      dataIndex: "lastSeen", // lastseen of relay status change
      key: "lastSeen",
    },
  ];

  return (
    <Content
      style={{
        margin: "24px 16px",
        paddingLeft: 20,
        paddingRight: 20,
        paddingTop: 30,
        paddingBottom: 30,
        minHeight: 280,
      }}
    >
      {/* Dashboard Overview Section */}
      <Row
        gutter={[40, 25]}
        style={{
          backgroundColor: "#fff",
          borderRadius: "8px",
          border: "1px solid #d9d9d9",
        }}
      >
        {/* Total Devices Card */}
        <Col
          xs={12}
          sm={12}
          md={6}
          lg={6}
          style={{
            padding: "20px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between", // Distribute space evenly
            height: "auto",
          }}
        >
          <Statistic
            title="Total Devices"
            value={totalDevices}
            prefix={<ApiOutlined />}
          />
        </Col>

        {/* Online Devices Card */}
        <Col
          xs={12}
          sm={12}
          md={6}
          lg={6}
          style={{
            padding: "20px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between", // Distribute space evenly
            height: "auto",
          }}
        >
          <Statistic
            title="Online"
            value={onlineDevices}
            prefix={<WifiOutlined />}
            valueStyle={{ color: "green" }}
          />
        </Col>

        {/* Offline Devices Card */}
        <Col
          xs={12}
          sm={12}
          md={6}
          lg={6}
          style={{
            padding: "20px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between", // Distribute space evenly
            height: "auto",
          }}
        >
          <Statistic
            title="Offline"
            value={offlineDevices}
            prefix={<ExclamationCircleOutlined />}
            valueStyle={{ color: "red" }}
          />
        </Col>

        {/* Maintenance Devices Card */}
        <Col
          xs={12}
          sm={12}
          md={6}
          lg={6}
          style={{
            padding: "20px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between", // Distribute space evenly
            height: "auto",
          }}
        >
          <Statistic
            title="Maintenance"
            value={maintenanceDevices}
            prefix={<ExclamationCircleOutlined />}
            valueStyle={{ color: "orange" }}
          />
        </Col>
      </Row>

      {/* Recent Sensor Readings Table Section */}
      <Row
        gutter={[40, 25]}
        style={{
          backgroundColor: "#fff",
          borderRadius: "8px",
          border: "1px solid #d9d9d9",
          paddingBottom: 20,
          marginTop: 20,
        }}
      >
        <Col span={24} style={{ marginTop: "20px" }}>
          <Title level={4}>Recent Sensor Readings</Title>
          <div
            style={{
              padding: "1px",
              backgroundColor: "#fff",
            }}
          >
            <Table
              columns={columns}
              dataSource={relayData} // Use relay data from API
              pagination={false}
              bordered
              scroll={{ x: true }} // Allow horizontal scrolling for small screens
            />
          </div>
        </Col>
      </Row>
    </Content>
  );
};

export default DashboardPage;
