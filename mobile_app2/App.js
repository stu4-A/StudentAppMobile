import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createStackNavigator } from "@react-navigation/stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Ionicons } from "@expo/vector-icons";
import { Provider as PaperProvider } from 'react-native-paper'; // Optional: for Material Design

// Import your screens (you'll need to create these)
import LoginScreen from "./screens/LoginScreen";
import DashboardScreen from "./screens/DashboardScreen";
import OpportunitiesScreen from "./screens/OpportunitiesScreen";
import ProfileScreen from "./screens/ProfileScreen";
import ApplicationsScreen from "./screens/ApplicationsScreen";
import GradesScreen from "./screens/GradesScreen";
import OpportunityDetailScreen from "./screens/OpportunityDetailScreen";
import SavedOpportunitiesScreen from "./screens/SavedOpportunitiesScreen";
import NotificationsScreen from "./screens/NotificationsScreen";

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Main app tabs after login
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === "Dashboard") {
            iconName = focused ? "home" : "home-outline";
          } else if (route.name === "Opportunities") {
            iconName = focused ? "briefcase" : "briefcase-outline";
          } else if (route.name === "Applications") {
            iconName = focused ? "document-text" : "document-text-outline";
          } else if (route.name === "Grades") {
            iconName = focused ? "school" : "school-outline";
          } else if (route.name === "Profile") {
            iconName = focused ? "person" : "person-outline";
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: "#007AFF",
        tabBarInactiveTintColor: "gray",
        tabBarStyle: {
          paddingVertical: 5,
          backgroundColor: "#ffffff",
        },
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{ title: "Dashboard" }}
      />
      <Tab.Screen 
        name="Opportunities" 
        component={OpportunitiesScreen}
        options={{ title: "Opportunities" }}
      />
      <Tab.Screen 
        name="Applications" 
        component={ApplicationsScreen}
        options={{ title: "My Applications" }}
      />
      <Tab.Screen 
        name="Grades" 
        component={GradesScreen}
        options={{ title: "Academic Records" }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{ title: "Profile" }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  return (
    <PaperProvider>
      <NavigationContainer>
        <Stack.Navigator 
          initialRouteName="Login"
          screenOptions={{
            headerStyle: {
              backgroundColor: "#007AFF",
            },
            headerTintColor: "#fff",
            headerTitleStyle: {
              fontWeight: "bold",
            },
            headerBackTitle: "Back",
          }}
        >
          <Stack.Screen 
            name="Login" 
            component={LoginScreen}
            options={{ 
              headerShown: false,
              title: "Student Login"
            }}
          />
          <Stack.Screen 
            name="MainTabs" 
            component={MainTabs}
            options={{ 
              headerShown: false,
              title: "Student App"
            }}
          />
          <Stack.Screen 
            name="OpportunityDetail" 
            component={OpportunityDetailScreen}
            options={{ title: "Opportunity Details" }}
          />
          <Stack.Screen 
            name="SavedOpportunities" 
            component={SavedOpportunitiesScreen}
            options={{ title: "Saved Opportunities" }}
          />
          <Stack.Screen 
            name="Notifications" 
            component={NotificationsScreen}
            options={{ title: "Notifications" }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </PaperProvider>
  );
}