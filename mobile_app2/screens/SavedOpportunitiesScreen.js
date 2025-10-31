import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { fetchSavedOpportunities, removeSavedOpportunity } from '../client';

const SavedOpportunitiesScreen = ({ navigation }) => {
  const [savedOpportunities, setSavedOpportunities] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadSavedOpportunities = async () => {
    try {
      const data = await fetchSavedOpportunities();
      setSavedOpportunities(data.results || data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load saved opportunities');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSavedOpportunities();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadSavedOpportunities();
    setRefreshing(false);
  };

  const handleRemoveSaved = async (savedOpportunityId) => {
    try {
      await removeSavedOpportunity(savedOpportunityId);
      setSavedOpportunities(prev => 
        prev.filter(item => item.id !== savedOpportunityId)
      );
      Alert.alert('Success', 'Opportunity removed from saved list');
    } catch (error) {
      Alert.alert('Error', 'Failed to remove opportunity');
    }
  };

  const renderSavedItem = ({ item }) => (
    <TouchableOpacity
      style={styles.opportunityCard}
      onPress={() => navigation.navigate('OpportunityDetail', { 
        opportunity: item.opportunity 
      })}
    >
      <View style={styles.cardHeader}>
        <View style={styles.companyInfo}>
          <Text style={styles.company}>{item.opportunity.company}</Text>
          <Text style={styles.role}>{item.opportunity.role}</Text>
        </View>
        <TouchableOpacity
          onPress={() => handleRemoveSaved(item.id)}
          style={styles.removeButton}
        >
          <Ionicons name="bookmark" size={24} color="#007AFF" />
        </TouchableOpacity>
      </View>
      
      <Text style={styles.field}>
        Required: {item.opportunity.field || 'Not specified'}
      </Text>
      
      <View style={styles.cardFooter}>
        <Text style={styles.deadline}>
          Deadline: {new Date(item.opportunity.deadline).toLocaleDateString()}
        </Text>
        <Text style={styles.savedDate}>
          Saved: {new Date(item.saved_at).toLocaleDateString()}
        </Text>
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.center}>
        <Text>Loading saved opportunities...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={savedOpportunities}
        renderItem={renderSavedItem}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Ionicons name="bookmark-outline" size={64} color="#ccc" />
            <Text style={styles.emptyText}>No saved opportunities</Text>
            <Text style={styles.emptySubtext}>
              Save opportunities to see them here
            </Text>
            <TouchableOpacity
              style={styles.browseButton}
              onPress={() => navigation.navigate('Opportunities')}
            >
              <Text style={styles.browseButtonText}>Browse Opportunities</Text>
            </TouchableOpacity>
          </View>
        }
        ListHeaderComponent={
          savedOpportunities.length > 0 && (
            <View style={styles.header}>
              <Text style={styles.headerText}>
                {savedOpportunities.length} saved opportunity{savedOpportunities.length !== 1 ? 'ies' : ''}
              </Text>
            </View>
          )
        }
      />
    </View>
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
  },
  listContent: {
    padding: 10,
  },
  header: {
    padding: 10,
    backgroundColor: '#fff',
    borderRadius: 8,
    marginBottom: 10,
  },
  headerText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  opportunityCard: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  companyInfo: {
    flex: 1,
  },
  company: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  role: {
    fontSize: 16,
    color: '#666',
    marginTop: 2,
  },
  removeButton: {
    padding: 4,
  },
  field: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  deadline: {
    fontSize: 12,
    color: '#999',
  },
  savedDate: {
    fontSize: 12,
    color: '#007AFF',
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
  },
  emptyText: {
    marginTop: 16,
    color: '#666',
    fontSize: 18,
    fontWeight: 'bold',
  },
  emptySubtext: {
    marginTop: 8,
    color: '#999',
    fontSize: 14,
    textAlign: 'center',
  },
  browseButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 6,
    marginTop: 16,
  },
  browseButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
});

export default SavedOpportunitiesScreen;