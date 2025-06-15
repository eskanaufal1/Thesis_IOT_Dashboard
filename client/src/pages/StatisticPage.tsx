import { ApiOutlined, CodeOutlined } from "@ant-design/icons";
import {
  Col,
  Row,
  Statistic,
  Grid,
  Card,
  Layout,
  Button,
  theme,
  Typography,
} from "antd";
import { LineChart } from "@mui/x-charts/LineChart";
import * as React from "react";
const { Content } = Layout;
const { Title } = Typography;
const { useBreakpoint } = Grid;

function StatisticPage() {
  const { token } = theme.useToken();
  const [cpuData, setCpuData] = React.useState<number[]>([]); // Dynamic CPU data
  const [voltageData, setVoltageData] = React.useState<number[]>([]); // Dummy data for Voltage
  const [currentData, setCurrentData] = React.useState<number[]>([]); // Dummy data for Current
  const [powerData, setPowerData] = React.useState<number[]>([]); // Dummy data for Power
  const [cpuUsage, setCpuUsage] = React.useState<number>(0); // Latest CPU usage value
  const [relayStatus, setRelayStatus] = React.useState([
    false,
    false,
    false,
    false,
  ]); // Relay on/off states
  const screens = useBreakpoint();

  // Function to generate random data between a given min and max
  const generateRandomData = (min: number, max: number) => {
    return Math.random() * (max - min) + min;
  };

  // Function to generate random CPU usage between 0 and 100
  const generateRandomCpuUsage = () => {
    return Math.random() * 100; // Random CPU usage value between 0 and 100
  };

  // Function to toggle relay state (on/off)
  const toggleRelay = (index: number) => {
    setRelayStatus((prevState) => {
      const newRelayStatus = [...prevState];
      newRelayStatus[index] = !newRelayStatus[index]; // Toggle state
      return newRelayStatus;
    });
  };

  // Calculate the number of active relays
  const activeRelays = relayStatus.filter((status) => status).length;

  // Update data every second
  React.useEffect(() => {
    const interval = setInterval(() => {
      const newCpuUsage = generateRandomCpuUsage(); // Generate random CPU usage
      setCpuUsage(newCpuUsage); // Update CPU usage stat

      // Update the CPU data array (keep last 20 data points)
      setCpuData((prevData) => {
        const newData = [...prevData, newCpuUsage];
        if (newData.length > 21) newData.shift(); // Keep only last 20 values
        return newData;
      });

      // Generate random data for each chart
      const newVoltageData = Array.from({ length: 20 }, () =>
        generateRandomData(210, 230)
      );
      const newCurrentData = Array.from({ length: 20 }, () =>
        generateRandomData(2, 7)
      );
      const newPowerData = Array.from({ length: 20 }, () =>
        generateRandomData(2, 6)
      );

      setVoltageData(newVoltageData);
      setCurrentData(newCurrentData);
      setPowerData(newPowerData);
    }, 1000); // Update every second

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, []);

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
      <Row gutter={[40, 25]}>
        <Col
          xs={24}
          sm={24}
          md={11}
          lg={11}
          push={0}
          style={{
            padding: "20px",
            backgroundColor: token.colorBgContainer,
            borderRadius: "8px", // Border radius to round the corners
            border: "1px solid #d9d9d9", // Border with a 1px solid color
          }}
        >
          <Card
            title={<Title level={4}>Device Statistics</Title>}
            style={{
              borderRadius: "8px",
              height: "100%", // Set height to 100% to match the server statistics card height
            }}
          >
            <Row justify={"center"}>
              <Col
                span={24}
                style={{
                  paddingTop: "0px",
                  display: "flex",
                  alignItems: "center", // Horizontally center
                  justifyContent:
                    screens.lg || screens.md ? "flex-start" : "center",
                  height: "100%", // Make the div take full height
                }}
              >
                <Statistic
                  title="Active Relays"
                  value={activeRelays} // Display active relays count
                  suffix={`/4`}
                  prefix={<ApiOutlined />}
                />
              </Col>
            </Row>
            <Row>
              <Col
                span={24}
                push={0}
                style={{
                  paddingTop: "0px",
                }}
              >
                <Row justify={"space-between"}>
                  {["Relay 1", "Relay 2", "Relay 3", "Relay 4"].map(
                    (relay, index) => (
                      <Col
                        xs={24}
                        sm={6}
                        md={6}
                        lg={6}
                        push={0}
                        key={index}
                        style={{
                          display: "flex",
                          flexDirection: "column", // Align title above button
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                      >
                        <Title level={5}>{relay}</Title>
                        <Button
                          type="primary"
                          danger={!relayStatus[index]}
                          style={{ width: "100%" }}
                          onClick={() => toggleRelay(index)}
                        >
                          {relayStatus[index] ? "On" : "Off"}
                        </Button>
                      </Col>
                    )
                  )}
                </Row>
              </Col>
            </Row>
          </Card>
        </Col>

        <Col
          xs={24}
          sm={24}
          md={12}
          lg={12}
          push={screens.lg || screens.md ? 1 : 0}
          style={{
            padding: "20px",
            backgroundColor: token.colorBgContainer,
            borderRadius: "8px", // Border radius to round the corners
            border: "1px solid #d9d9d9", // Border with a 1px solid color
          }}
        >
          <Card
            title={<Title level={4}>Server Statistics</Title>}
            style={{
              borderRadius: "8px",
              height: "100%", // Set height to 100% to match the relay statistics card height
            }}
          >
            <Row justify="space-between" align="middle">
              <Col>
                <Statistic
                  title="CPU"
                  value={`${cpuUsage.toFixed(0)}%`} // Display CPU usage with 2 decimal places
                  suffix="/ 100%"
                  prefix={<CodeOutlined />}
                />
              </Col>
              <Col>
                <div style={{ textAlign: "center" }}>
                  <Title level={4} style={{ marginTop: 10 }}>
                    CPU Usage Graph
                  </Title>
                </div>
              </Col>
            </Row>

            {/* Real-time CPU usage graph */}
            <LineChart
              height={200}
              margin={{ left: -10, bottom: 0 }}
              xAxis={[{ data: Array.from({ length: 21 }, (_, i) => i) }]}
              series={[
                {
                  data: cpuData, // Last 20 CPU usage data points
                  valueFormatter: (value) =>
                    value == null ? "?" : value.toString(),
                  showMark: false,
                  label: "CPU Usage",
                  color: "#1890ff",
                  area: true, // Fill the area under the line
                },
              ]}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[40, 25]} style={{ marginTop: "20px" }}>
        <Col
          push={0}
          style={{
            padding: "0px",
            borderRadius: "8px", // Border radius to round the corners
            border: "1px solid #d9d9d9", // Border with a 1px solid color
          }}
          xs={24}
          sm={24}
          md={11}
          lg={11}
        >
          {/* Voltage LineChart */}
          <Card
            title={<Title level={4}>Voltage Statistics</Title>}
            style={{
              borderRadius: "8px",
              padding: "20px",
              backgroundColor: token.colorBgContainer,
            }}
          >
            <LineChart
              height={150}
              margin={{ left: -10, bottom: 0 }}
              xAxis={[
                {
                  data: [
                    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
                    18, 19, 20,
                  ],
                },
              ]}
              series={[
                {
                  data: voltageData, // Use the moving data for voltage
                  valueFormatter: (value) =>
                    value == null ? "NaN" : value.toString(),
                },
              ]}
            />
          </Card>

          {/* Current LineChart */}
          <Card
            title={<Title level={4}>Current Statistics</Title>}
            style={{
              borderRadius: "8px",
              padding: "20px",
              backgroundColor: token.colorBgContainer,
            }}
          >
            <LineChart
              hideLegend={true}
              height={150}
              margin={{ left: -20, bottom: 0 }}
              xAxis={[
                {
                  data: [
                    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
                    18, 19, 20,
                  ],
                },
              ]}
              series={[
                {
                  data: currentData, // Use the moving data for current
                  valueFormatter: (value) =>
                    value == null ? "?" : value.toString(),
                  showMark: false,
                  label: "Relay 1",
                  color: "#1890ff",
                },
              ]}
            />
          </Card>
        </Col>

        {/* Power LineChart */}
        <Col
          xs={24}
          sm={24}
          md={12}
          lg={12}
          push={screens.lg || screens.md ? 1 : 0}
          style={{
            padding: "0px",
            backgroundColor: token.colorBgContainer,
            borderRadius: "8px", // Border radius to round the corners
            border: "1px solid #d9d9d9", // Border with a 1px solid color
          }}
        >
          <Card
            title={<Title level={4}>Power Statistics</Title>}
            style={{
              borderRadius: "8px",
              padding: "0px",
              backgroundColor: token.colorBgContainer,
            }}
          >
            <LineChart
              hideLegend={true}
              margin={{ left: -20, bottom: 0 }}
              xAxis={[
                {
                  data: [
                    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
                    18, 19, 20,
                  ],
                },
              ]}
              series={[
                {
                  data: powerData, // Use the moving data for power
                  valueFormatter: (value) =>
                    value == null ? "?" : value.toString(),
                  showMark: false,
                  label: "Relay 1",
                  color: "#1890ff",
                },
              ]}
              height={400}
            />
          </Card>
        </Col>
      </Row>
    </Content>
  );
}

export default StatisticPage;
