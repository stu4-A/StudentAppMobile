import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  RefreshControl,
  Alert,
  SectionList,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { fetchGrades, fetchGPA, fetchSemesters } from '../client';

const GradesScreen = () => {
  const [grades, setGrades] = useState([]);
  const [gpaData, setGpaData] = useState(null);
  const [semesters, setSemesters] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const [gradesData, gpa, semestersData] = await Promise.all([
        fetchGrades(),
        fetchGPA(),
        fetchSemesters(),
      ]);
      setGrades(gradesData.results || gradesData);
      setGpaData(gpa);
      setSemesters(semestersData.results || semestersData);
    } catch (error) {
      Alert.alert('Error', 'Failed to load academic data');
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

  // Group grades by semester
  const groupedGrades = grades.reduce((acc, grade) => {
    const semesterName = grade.semester ? 
      `${grade.semester.year} - ${grade.semester.name}` : 'No Semester';
    if (!acc[semesterName]) {
      acc[semesterName] = [];
    }
    acc[semesterName].push(grade);
    return acc;
  }, {});

  const sections = Object.keys(groupedGrades).map(semester => ({
    title: semester,
    data: groupedGrades[semester],
  }));

  const getGradeColor = (grade) => {
    switch (grade) {
      case 'A': return '#4CAF50';
      case 'B+': return '#8BC34A';
      case 'B': return '#CDDC39';
      case 'C+': return '#FFC107';
      case 'C': return '#FF9800';
      case 'D': return '#F44336';
      case 'F': return '#D32F2F';
      default: return '#666';
    }
  };

  const renderGradeItem = ({ item }) => (
    <View style={styles.gradeItem}>
      <View style={styles.gradeInfo}>
        <Text style={styles.courseName}>{item.course_unit}</Text>
        <Text style={styles.courseScore}>Score: {item.score}%</Text>
      </View>
      <View style={[styles.gradeBadge, { backgroundColor: getGradeColor(item.grade) }]}>
        <Text style={styles.gradeText}>{item.grade}</Text>
      </View>
    </View>
  );

  const renderSectionHeader = ({ section }) => (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionTitle}>{section.title}</Text>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.center}>
        <Text>Loading academic records...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* GPA Summary */}
      <View style={styles.gpaSection}>
        <View style={styles.gpaCard}>
          <View style={styles.gpaItem}>
            <Ionicons name="school" size={32} color="#007AFF" />
            <Text style={styles.gpaLabel}>Current GPA</Text>
            <Text style={styles.gpaValue}>{gpaData?.gpa || '0.0'}</Text>
          </View>
          <View style={styles.gpaDivider} />
          <View style={styles.gpaItem}>
            <Ionicons name="trending-up" size={32} color="#4CAF50" />
            <Text style={styles.gpaLabel}>Cumulative GPA</Text>
            <Text style={styles.gpaValue}>{gpaData?.cgpa || '0.0'}</Text>
          </View>
        </View>
      </View>

      {/* Grades List */}
      <SectionList
        sections={sections}
        renderItem={renderGradeItem}
        renderSectionHeader={renderSectionHeader}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Ionicons name="school-outline" size={64} color="#ccc" />
            <Text style={styles.emptyText}>No grades recorded</Text>
            <Text style={styles.emptySubtext}>
              Your grades will appear here once uploaded
            </Text>
          </View>
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
  gpaSection: {
    padding: 10,
  },
  gpaCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  gpaItem: {
    alignItems: 'center',
    flex: 1,
  },
  gpaDivider: {
    width: 1,
    height: '80%',
    backgroundColor: '#eee',
  },
  gpaLabel: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
    marginBottom: 4,
  },
  gpaValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  listContent: {
    padding: 10,
  },
  sectionHeader: {
    backgroundColor: '#007AFF',
    padding: 10,
    borderRadius: 6,
    marginBottom: 8,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  gradeItem: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 6,
    marginBottom: 6,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  gradeInfo: {
    flex: 1,
  },
  courseName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  courseScore: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  gradeBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    minWidth: 40,
    alignItems: 'center',
  },
  gradeText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
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
});

export default GradesScreen;