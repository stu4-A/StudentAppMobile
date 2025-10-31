import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createStackNavigator } from "@react-navigation/stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Ionicons } from "@expo/vector-icons";
import LoginScreen from "./screens/LoginScreen";
import DashboardScreen from "./screens/DashboardScreen";
import OpportunitiesScreen from "./screens/OpportunitiesScreen";
import ProfileScreen from "./screens/ProfileScreen";
import ApplicationsScreen from "./screens/ApplicationsScreen";
import GradesScreen from "./screens/GradesScreen";
import OpportunityDetailScreen from "./screens/OpportunityDetailScreen";

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
        tabBarActiveTintColor: "tomato",
        tabBarInactiveTintColor: "gray",
      })}
    >
      <Tab.Screen name="Dashboard" component={DashboardScreen} />
      <Tab.Screen name="Opportunities" component={OpportunitiesScreen} />
      <Tab.Screen name="Applications" component={ApplicationsScreen} />
      <Tab.Screen name="Grades" component={GradesScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator 
        initialRouteName="Login"
        screenOptions={{
          headerStyle: {
            backgroundColor: '#f4511e',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        <Stack.Screen 
          name="Login" 
          component={LoginScreen}
          options={{ headerShown: false }}
        />
        <Stack.Screen 
          name="MainTabs" 
          component={MainTabs}
          options={{ headerShown: false }}
        />
        <Stack.Screen 
          name="OpportunityDetail" 
          component={OpportunityDetailScreen}
          options={{ title: 'Opportunity Details' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}