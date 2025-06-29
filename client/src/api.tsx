// src/api.ts

import axios from "axios";

// Create an Axios instance with the base URL
const apiClient = axios.create({
  baseURL: "http://localhost:3000", // Replace this with your API's base URL
  headers: {
    "Content-Type": "application/json",
  },
});

// Optionally, you can add request/response interceptors for error handling or authentication
apiClient.interceptors.request.use(
  (config) => {
    // You can add authentication token or other headers here
    // For example, adding a JWT token to the Authorization header
    const token = localStorage.getItem("authToken"); // Replace with actual token logic
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Optional: Add response interceptor if needed
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle errors globally here
    console.error("API Error:", error);
    return Promise.reject(error);
  }
);

export default apiClient;
