import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { fetchDashboard, fetchDashboardStats } from '../client';

const DashboardScreen = ({ navigation }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [stats, setStats] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const [dashboard, statsData] = await Promise.all([
        fetchDashboard(),
        fetchDashboardStats(),
      ]);
      setDashboardData(dashboard);
      setStats(statsData);
    } catch (error) {
      console.error('Dashboard load error:', error);
      Alert.alert('Error', 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const StatCard = ({ title, value, icon, color, onPress }) => (
    <TouchableOpacity 
      style={[styles.statCard, { borderLeftColor: color }]} 
      onPress={onPress}
    >
      <View style={styles.statHeader}>
        <Ionicons name={icon} size={24} color={color} />
        <Text style={styles.statValue}>{value}</Text>
      </View>
      <Text style={styles.statTitle}>{title}</Text>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading dashboard...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.welcome}>
          Welcome, {dashboardData?.user_profile?.user?.username || 'Student'}!
        </Text>
        <Text style={styles.subtitle}>Here's your overview</Text>
      </View>

      {/* Stats Grid */}
      <View style={styles.statsGrid}>
        <StatCard
          title="GPA"
          value={stats?.academic?.gpa || '0.0'}
          icon="school"
          color="#4CAF50"
          onPress={() => navigation.navigate('Grades')}
        />
        <StatCard
          title="Applications"
          value={stats?.opportunities?.applied || 0}
          icon="document-text"
          color="#FF9800"
          onPress={() => navigation.navigate('Applications')}
        />
        <StatCard
          title="Saved Jobs"
          value={stats?.opportunities?.saved || 0}
          icon="bookmark"
          color="#2196F3"
          onPress={() => navigation.navigate('SavedOpportunities')}
        />
        <StatCard
          title="Notifications"
          value={dashboardData?.unread_notifications || 0}
          icon="notifications"
          color="#F44336"
          onPress={() => navigation.navigate('Notifications')}
        />
      </View>

      {/* Recent Opportunities */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Recent Opportunities</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Opportunities')}>
            <Text style={styles.seeAll}>See All</Text>
          </TouchableOpacity>
        </View>
        
        {dashboardData?.recent_opportunities?.map((opportunity) => (
          <TouchableOpacity
            key={opportunity.id}
            style={styles.opportunityCard}
            onPress={() => navigation.navigate('OpportunityDetail', { opportunity })}
          >
            <Text style={styles.company}>{opportunity.company}</Text>
            <Text style={styles.role}>{opportunity.role}</Text>
            <Text style={styles.deadline}>
              Deadline: {new Date(opportunity.deadline).toLocaleDateString()}
            </Text>
          </TouchableOpacity>
        ))}
        
        {(!dashboardData?.recent_opportunities || dashboardData.recent_opportunities.length === 0) && (
          <View style={styles.emptyState}>
            <Ionicons name="briefcase-outline" size={40} color="#ccc" />
            <Text style={styles.noData}>No recent opportunities</Text>
            <TouchableOpacity
              style={styles.browseButton}
              onPress={() => navigation.navigate('Opportunities')}
            >
              <Text style={styles.browseButtonText}>Browse Opportunities</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionsGrid}>
          <TouchableOpacity 
            style={styles.actionButton}
            onPress={() => navigation.navigate('Opportunities')}
          >
            <Ionicons name="briefcase" size={24} color="#007AFF" />
            <Text style={styles.actionText}>Browse Jobs</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.actionButton}
            onPress={() => navigation.navigate('Grades')}
          >
            <Ionicons name="school" size={24} color="#4CAF50" />
            <Text style={styles.actionText}>View Grades</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.actionButton}
            onPress={() => navigation.navigate('Profile')}
          >
            <Ionicons name="person" size={24} color="#FF9800" />
            <Text style={styles.actionText}>My Profile</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.actionButton}
            onPress={() => navigation.navigate('Applications')}
          >
            <Ionicons name="document-text" size={24} color="#2196F3" />
            <Text style={styles.actionText}>Applications</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
    fontSize: 16,
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  welcome: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 4,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 10,
    justifyContent: 'space-between',
  },
  statCard: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
    width: '48%',
    marginBottom: 10,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  statHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  statTitle: {
    fontSize: 14,
    color: '#666',
  },
  section: {
    backgroundColor: '#fff',
    margin: 10,
    padding: 15,
    borderRadius: 8,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  seeAll: {
    color: '#007AFF',
    fontSize: 14,
    fontWeight: '600',
  },
  opportunityCard: {
    backgroundColor: '#f9f9f9',
    padding: 12,
    borderRadius: 6,
    marginBottom: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#007AFF',
  },
  company: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  role: {
    fontSize: 14,
    color: '#666',
    marginVertical: 2,
  },
  deadline: {
    fontSize: 12,
    color: '#999',
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  noData: {
    textAlign: 'center',
    color: '#999',
    fontStyle: 'italic',
    marginTop: 8,
    marginBottom: 16,
  },
  browseButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 6,
  },
  browseButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionButton: {
    backgroundColor: '#f8f9fa',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    width: '48%',
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  actionText: {
    marginTop: 8,
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
    textAlign: 'center',
  },
});

export default DashboardScreen;