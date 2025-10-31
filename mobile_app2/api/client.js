import axios from "axios";

/**
 * If you are testing on your phone (Expo Go):
 * - Run `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
 * - Copy your local network IP address, e.g. 192.168.1.102
 * - Replace it below.
 * 
 * When you deploy or switch to Render, comment out the local line and
 * uncomment the Render URL.
 */

// 🔹 LOCAL TESTING (Django on your machine)
// const API_BASE_URL = "http://127.0.0.1:8000/api";

// 🔹 RENDER DEPLOYMENT (when Django backend is live)
const API_BASE_URL = "https://studentappmobile.onrender.com/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

// Add request interceptor to include token in all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      // If you're using React Native, you might want to navigate to login screen
      // For web, you can redirect to login page
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// -------------------------
// Authentication API calls
// -------------------------
export const loginUser = async (username, password) => {
  const response = await api.post("/token/", { username, password });
  return response.data;
};

// -------------------------
// Dashboard Data Fetch
// -------------------------
export const fetchDashboard = async () => {
  const response = await api.get("/dashboard/");
  return response.data;
};

export const fetchDashboardStats = async () => {
  const response = await api.get("/dashboard/stats/");
  return response.data;
};

// -------------------------
// User Profile APIs
// -------------------------
export const fetchUserProfile = async () => {
  const response = await api.get("/user-profiles/my_profile/");
  return response.data;
};

export const updateUserProfile = async (profileData) => {
  const response = await api.patch("/user-profiles/my_profile/", profileData);
  return response.data;
};

// -------------------------
// Student Profile APIs
// -------------------------
export const fetchStudentProfile = async () => {
  const response = await api.get("/student-profiles/my_student_profile/");
  return response.data;
};

export const updateStudentProfile = async (profileData) => {
  const response = await api.patch("/student-profiles/my_student_profile/", profileData);
  return response.data;
};

// -------------------------
// Career Opportunities APIs
// -------------------------
export const fetchOpportunities = async () => {
  const response = await api.get("/opportunities/");
  return response.data;
};

export const fetchOpportunity = async (id) => {
  const response = await api.get(`/opportunities/${id}/`);
  return response.data;
};

export const saveOpportunity = async (opportunityId) => {
  const response = await api.post(`/opportunities/${opportunityId}/save_opportunity/`);
  return response.data;
};

export const applyForOpportunity = async (opportunityId, coverLetter = "") => {
  const response = await api.post(`/opportunities/${opportunityId}/apply/`, {
    cover_letter: coverLetter
  });
  return response.data;
};

// -------------------------
// Saved Opportunities APIs
// -------------------------
export const fetchSavedOpportunities = async () => {
  const response = await api.get("/saved-opportunities/");
  return response.data;
};

export const removeSavedOpportunity = async (savedOpportunityId) => {
  const response = await api.delete(`/saved-opportunities/${savedOpportunityId}/`);
  return response.data;
};

// -------------------------
// Applications APIs
// -------------------------
export const fetchApplications = async () => {
  const response = await api.get("/applications/");
  return response.data;
};

export const fetchApplication = async (id) => {
  const response = await api.get(`/applications/${id}/`);
  return response.data;
};

// -------------------------
// Notifications APIs
// -------------------------
export const fetchNotifications = async () => {
  const response = await api.get("/notifications/");
  return response.data;
};

export const markNotificationAsRead = async (notificationId) => {
  const response = await api.post(`/notifications/${notificationId}/mark_read/`);
  return response.data;
};

// -------------------------
// Academic APIs
// -------------------------
export const fetchSemesters = async () => {
  const response = await api.get("/semesters/");
  return response.data;
};

export const fetchCourseUnits = async () => {
  const response = await api.get("/course-units/");
  return response.data;
};

export const fetchGrades = async () => {
  const response = await api.get("/grades/");
  return response.data;
};

export const fetchGPA = async () => {
  const response = await api.get("/grades/my_gpa/");
  return response.data;
};

export const addGrade = async (gradeData) => {
  const response = await api.post("/grades/", gradeData);
  return response.data;
};

// -------------------------
// Reports APIs
// -------------------------
export const fetchReports = async () => {
  const response = await api.get("/reports/");
  return response.data;
};

export const generateReport = async (reportData) => {
  const response = await api.post("/reports/", reportData);
  return response.data;
};

// -------------------------
// Utility Functions
// -------------------------
export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem('token', token);
    // For React Native, you might use AsyncStorage instead
    // await AsyncStorage.setItem('token', token);
  } else {
    localStorage.removeItem('token');
    // await AsyncStorage.removeItem('token');
  }
};

export const getAuthToken = () => {
  return localStorage.getItem('token');
  // For React Native: return await AsyncStorage.getItem('token');
};

export const logoutUser = () => {
  localStorage.removeItem('token');
  // For React Native: await AsyncStorage.removeItem('token');
  // If web, redirect to login
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
};