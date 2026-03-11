import React from 'react';
import { View, Text, StyleSheet, FlatList } from 'react-native';
import { colors, spacing, typography } from '../../theme/theme';
import { DiscoveryCard } from '../../components/DiscoveryCard';

const mockData = [
  { id: '1', name: 'Teddy Bear', category: 'Toys', time: '10:00 AM' },
  { id: '2', name: 'Fire Engine', category: 'Vehicles', time: 'Yesterday' },
  { id: '3', name: 'Coffee Mug', category: 'Household Objects', time: 'Mon, 12:00 PM' },
  { id: '4', name: 'House Cat', category: 'Animals', time: 'Sun, 4:00 PM' },
];

const DiscoveriesScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.header}>All Discoveries</Text>
      
      {/* Search and Filter Chips placeholder */}
      <View style={styles.filterBar}>
        <Text style={styles.filterText}>Filtering: 4 found</Text>
      </View>

      <FlatList
        data={mockData}
        numColumns={2}
        keyExtractor={item => item.id}
        columnWrapperStyle={styles.row}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => (
          <View style={styles.cardContainer}>
            <DiscoveryCard 
              name={item.name} 
              category={item.category} 
              timestamp={item.time} 
              onPress={() => {}} 
            />
          </View>
        )}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, padding: spacing.lg },
  header: { ...typography.h1, color: colors.textPrimary, marginBottom: spacing.md },
  filterBar: { marginBottom: spacing.lg, paddingBottom: spacing.sm, borderBottomWidth: 1, borderColor: colors.border },
  filterText: { ...typography.body, color: colors.textSecondary },
  list: { paddingBottom: spacing.xxl },
  row: { justifyContent: 'space-between' },
  cardContainer: { width: '48%' }
});

export default DiscoveriesScreen;
