import {
  ApiOutlined,
  WifiOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  EditOutlined,
  DeleteOutlined,
} from "@ant-design/icons";
import {
  Col,
  Row,
  Statistic,
  Grid,
  Layout,
  Typography,
  Card,
  Button,
  Modal,
  Select,
  Input,
} from "antd";
import React, { useState } from "react";

const { Content } = Layout;
const { Title } = Typography;
const { useBreakpoint } = Grid;
const { Option } = Select;

const DevicePage = () => {
  const screens = useBreakpoint();
  const [isAddDeviceModalOpen, setIsAddDeviceModalOpen] = useState(false);
  const [isEditDeviceModalOpen, setIsEditDeviceModalOpen] = useState(false);
  const [devices, setDevices] = useState([
    {
      key: "1",
      deviceName: "Device Name 1",
      status: "Online", // Adding status
      location: "Living Room",
      relay1: "On",
      relay2: "Off",
      relay3: "On",
      relay4: "Off",
      lastSeen: "13/06/2025, 03:10:09",
    },
    {
      key: "2",
      deviceName: "Device Name 2",
      status: "Online", // Adding status
      location: "Bedroom",
      relay1: "Off",
      relay2: "On",
      relay3: "Off",
      relay4: "On",
      lastSeen: "13/06/2025, 01:10:08",
    },
    // More devices...
  ]);
  const [newDevice, setNewDevice] = useState({
    deviceName: "",
    status: "Offline", // Default status to "Offline"
    location: "",
    relay1: "Off",
    relay2: "Off",
    relay3: "Off",
    relay4: "Off",
  });
  const [editDevice, setEditDevice] = useState<any>({});

  // Add Device Modal Handler
  const handleAddDeviceOk = () => {
    setDevices([
      ...devices,
      {
        key: devices.length + 1 + "",
        ...newDevice,
        lastSeen: new Date().toLocaleString(),
      },
    ]);
    setIsAddDeviceModalOpen(false);
  };

  const handleAddDeviceCancel = () => {
    setIsAddDeviceModalOpen(false);
  };

  // Edit Device Modal Handler
  const handleEditDeviceOk = () => {
    const updatedDevices = devices.map((device) =>
      device.key === editDevice.key ? editDevice : device
    );
    setDevices(updatedDevices);
    setIsEditDeviceModalOpen(false);
  };

  const handleEditDeviceCancel = () => {
    setIsEditDeviceModalOpen(false);
  };

  // Delete Device Handler
  const handleDeleteDevice = (key: string) => {
    setDevices(devices.filter((device) => device.key !== key));
  };

  // Handle Relay Change
  const handleRelayChange = (value: string, relay: string) => {
    setEditDevice((prevDevice: any) => ({
      ...prevDevice,
      [relay]: value,
    }));
  };

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
      {/* Header with Title and Add Device Button */}
      <Row justify="space-between" style={{ marginBottom: 20 }}>
        <Col>
          <Title level={3}>Device Page</Title>
        </Col>
        <Col>
          <Button
            type="primary"
            icon={<EditOutlined />}
            style={{ marginTop: "8px" }}
            onClick={() => setIsAddDeviceModalOpen(true)}
          >
            Add Device
          </Button>
        </Col>
      </Row>

      {/* Dashboard Overview Section */}
      <Row gutter={[40, 25]}>
        {devices.map((device) => (
          <Col
            xs={24}
            sm={24}
            md={24}
            lg={8}
            key={device.key}
            style={{
              padding: "20px",
              backgroundColor: "#fff",
              borderRadius: "8px",
              border: "1px solid #d9d9d9",
              display: "flex",
              flexDirection: "column",
              marginBottom: "20px", // Adding gap between devices
              marginRight: 20,
            }}
          >
            <Card
              title={device.deviceName}
              extra={
                <div>
                  <Button
                    shape="circle"
                    icon={<EditOutlined />}
                    style={{ marginRight: "10px" }}
                    onClick={() => {
                      setEditDevice(device);
                      setIsEditDeviceModalOpen(true);
                    }}
                  />
                  <Button
                    shape="circle"
                    icon={<DeleteOutlined />}
                    onClick={() => handleDeleteDevice(device.key)}
                  />
                </div>
              }
            >
              <Row>
                <Col span={24}>
                  <Statistic
                    title="Status"
                    value={device.status}
                    valueStyle={{
                      color: device.status === "Online" ? "green" : "red",
                    }}
                    prefix={
                      device.status === "Online" ? (
                        <WifiOutlined style={{ color: "green" }} />
                      ) : (
                        <ExclamationCircleOutlined style={{ color: "red" }} />
                      )
                    }
                  />
                </Col>
              </Row>

              <Row>
                <Col span={24}>
                  <Title level={5}>Location: {device.location}</Title>
                </Col>
              </Row>

              <Row>
                <Col span={24}>
                  <Title level={5}>Last Seen: {device.lastSeen}</Title>
                </Col>
              </Row>

              {/* Relay Statuses with Icons */}
              <Row gutter={[8, 8]}>
                <Col span={12}>
                  <Title level={5}>Relay 1</Title>
                  {device.relay1 === "On" ? (
                    <CheckCircleOutlined
                      style={{ color: "blue", fontSize: "24px" }}
                    />
                  ) : (
                    <CloseCircleOutlined
                      style={{ color: "red", fontSize: "24px" }}
                    />
                  )}
                </Col>

                <Col span={12}>
                  <Title level={5}>Relay 2</Title>
                  {device.relay2 === "On" ? (
                    <CheckCircleOutlined
                      style={{ color: "blue", fontSize: "24px" }}
                    />
                  ) : (
                    <CloseCircleOutlined
                      style={{ color: "red", fontSize: "24px" }}
                    />
                  )}
                </Col>

                <Col span={12}>
                  <Title level={5}>Relay 3</Title>
                  {device.relay3 === "On" ? (
                    <CheckCircleOutlined
                      style={{ color: "blue", fontSize: "24px" }}
                    />
                  ) : (
                    <CloseCircleOutlined
                      style={{ color: "red", fontSize: "24px" }}
                    />
                  )}
                </Col>

                <Col span={12}>
                  <Title level={5}>Relay 4</Title>
                  {device.relay4 === "On" ? (
                    <CheckCircleOutlined
                      style={{ color: "blue", fontSize: "24px" }}
                    />
                  ) : (
                    <CloseCircleOutlined
                      style={{ color: "red", fontSize: "24px" }}
                    />
                  )}
                </Col>
              </Row>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Add Device Modal */}
      <Modal
        title="Add New Device"
        open={isAddDeviceModalOpen}
        onOk={handleAddDeviceOk}
        onCancel={handleAddDeviceCancel}
      >
        <Input
          placeholder="Device Name"
          value={newDevice.deviceName}
          onChange={(e) =>
            setNewDevice({ ...newDevice, deviceName: e.target.value })
          }
          style={{ marginBottom: 10 }}
        />
        <Input
          placeholder="Location"
          value={newDevice.location}
          onChange={(e) =>
            setNewDevice({ ...newDevice, location: e.target.value })
          }
          style={{ marginBottom: 10 }}
        />
        {/* Relay Statuses */}
        <Select
          value={newDevice.relay1}
          onChange={(value) => setNewDevice({ ...newDevice, relay1: value })}
          style={{ width: "100%", marginBottom: 10 }}
        >
          <Option value="On">On</Option>
          <Option value="Off">Off</Option>
        </Select>
        <Select
          value={newDevice.relay2}
          onChange={(value) => setNewDevice({ ...newDevice, relay2: value })}
          style={{ width: "100%", marginBottom: 10 }}
        >
          <Option value="On">On</Option>
          <Option value="Off">Off</Option>
        </Select>
        <Select
          value={newDevice.relay3}
          onChange={(value) => setNewDevice({ ...newDevice, relay3: value })}
          style={{ width: "100%", marginBottom: 10 }}
        >
          <Option value="On">On</Option>
          <Option value="Off">Off</Option>
        </Select>
        <Select
          value={newDevice.relay4}
          onChange={(value) => setNewDevice({ ...newDevice, relay4: value })}
          style={{ width: "100%", marginBottom: 10 }}
        >
          <Option value="On">On</Option>
          <Option value="Off">Off</Option>
        </Select>
      </Modal>

      {/* Edit Device Modal */}
      <Modal
        title="Edit Device"
        open={isEditDeviceModalOpen}
        onOk={handleEditDeviceOk}
        onCancel={handleEditDeviceCancel}
      >
        <Input
          placeholder="Device Name"
          value={editDevice.deviceName}
          onChange={(e) =>
            setEditDevice({ ...editDevice, deviceName: e.target.value })
          }
          style={{ marginBottom: 10 }}
        />
        <Input
          placeholder="Location"
          value={editDevice.location}
          onChange={(e) =>
            setEditDevice({ ...editDevice, location: e.target.value })
          }
          style={{ marginBottom: 10 }}
        />
        {/* Relay Statuses */}
        <Select
          value={editDevice.relay1}
          onChange={(value) => handleRelayChange(value, "relay1")}
          style={{ width: "100%", marginBottom: 10 }}
        >
          <Option value="On">On</Option>
          <Option value="Off">Off</Option>
        </Select>
        <Select
          value={editDevice.relay2}
          onChange={(value) => handleRelayChange(value, "relay2")}
          style={{ width: "100%", marginBottom: 10 }}
        >
          <Option value="On">On</Option>
          <Option value="Off">Off</Option>
        </Select>
        <Select
          value={editDevice.relay3}
          onChange={(value) => handleRelayChange(value, "relay3")}
          style={{ width: "100%", marginBottom: 10 }}
        >
          <Option value="On">On</Option>
          <Option value="Off">Off</Option>
        </Select>
        <Select
          value={editDevice.relay4}
          onChange={(value) => handleRelayChange(value, "relay4")}
          style={{ width: "100%", marginBottom: 10 }}
        >
          <Option value="On">On</Option>
          <Option value="Off">Off</Option>
        </Select>
      </Modal>
    </Content>
  );
};

export default DevicePage;
