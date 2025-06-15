import {
  ApiOutlined,
  WifiOutlined,
  ExclamationCircleOutlined,
} from "@ant-design/icons";
import { Col, Row, Statistic, Grid, Layout, Typography, Table } from "antd";

const { Content } = Layout;
const { Title } = Typography;
const { useBreakpoint } = Grid;

const DashboardPage = () => {
  const screens = useBreakpoint();

  // Dummy Data
  const totalDevices = 5;
  const onlineDevices = 4;
  const offlineDevices = 1;
  const maintenanceDevices = 0;

  // Dummy relay data (Relay 1, 2, 3, 4 status)
  const relayData = [
    {
      key: "1",
      relay1: "On",
      relay2: "Off",
      relay3: "On",
      relay4: "Off",
      timestamp: "13/06/2025, 03:10:09",
    },
    {
      key: "2",
      relay1: "Off",
      relay2: "On",
      relay3: "Off",
      relay4: "On",
      timestamp: "13/06/2025, 01:10:08",
    },
    {
      key: "3",
      relay1: "On",
      relay2: "On",
      relay3: "Off",
      relay4: "Off",
      timestamp: "12/06/2025, 21:10:09",
    },
    {
      key: "4",
      relay1: "Off",
      relay2: "Off",
      relay3: "On",
      relay4: "On",
      timestamp: "12/06/2025, 19:10:09",
    },
    {
      key: "5",
      relay1: "On",
      relay2: "Off",
      relay3: "On",
      relay4: "Off",
      timestamp: "12/06/2025, 18:10:09",
    },
  ];

  const columns = [
    {
      title: "Device ID",
      dataIndex: "key", // Use the key as the device identifier
      key: "key",
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
      title: "Timestamp",
      dataIndex: "timestamp", // Timestamp of relay status change
      key: "timestamp",
    },
  ];

  return (
    <Content
      style={{
        margin: "24px 16px",
        paddingLeft: 50,
        paddingRight: 50,
        paddingTop: 30,
        paddingBottom: 30,
        minHeight: 280,
      }}
    >
      {/* Dashboard Overview Section */}
      <Row gutter={[40, 25]}>
        {/* Total Devices Card */}
        <Col
          xs={24}
          sm={24}
          md={6}
          lg={6}
          style={{
            padding: "20px",
            backgroundColor: "#fff",
            borderRadius: "8px",
            border: "1px solid #d9d9d9",
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
          xs={24}
          sm={24}
          md={6}
          lg={6}
          style={{
            padding: "20px",
            backgroundColor: "#fff",
            borderRadius: "8px",
            border: "1px solid #d9d9d9",
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
          xs={24}
          sm={24}
          md={6}
          lg={6}
          style={{
            padding: "20px",
            backgroundColor: "#fff",
            borderRadius: "8px",
            border: "1px solid #d9d9d9",
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
          xs={24}
          sm={24}
          md={6}
          lg={6}
          style={{
            padding: "20px",
            backgroundColor: "#fff",
            borderRadius: "8px",
            border: "1px solid #d9d9d9",
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
              padding: "20px",
              backgroundColor: "#fff",
              // borderRadius: "8px",
              // border: "1px solid #d9d9d9",
            }}
          >
            <Table
              columns={columns}
              dataSource={relayData} // Update to use relay data
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
