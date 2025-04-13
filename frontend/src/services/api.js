import axios from "axios";

// Set up your backend URL
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Function to query the financial data
export const getFinancialData = async (query) => {
  try {
    const response = await axios.post(`${API_URL}/query-financial-data`, {
      query,
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching financial data", error);
    throw error;
  }
};
