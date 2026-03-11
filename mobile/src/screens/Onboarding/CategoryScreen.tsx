import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { PrimaryButton } from '../../components/PrimaryButton';
import { colors, spacing, typography, radii } from '../../theme/theme';
import { ChildSettings } from '../../types/settings';

const CategoryScreen = ({ navigation }: any) => {
  const [selectedCats, setSelectedCats] = useState<Set<string>>(new Set(['animals', 'toys', 'vehicles']));

  const categories: { id: ChildSettings['allowedCategories'][0], title: string }[] = [
    { id: 'animals', title: 'Animals' },
    { id: 'vehicles', title: 'Vehicles' },
    { id: 'toys', title: 'Toys' },
    { id: 'household_objects', title: 'Household Objects' },
  ];

  const toggleCategory = (id: string) => {
    const newCats = new Set(selectedCats);
    if (newCats.has(id)) newCats.delete(id);
    else newCats.add(id);
    setSelectedCats(newCats);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Safe Categories</Text>
      <Text style={styles.subtext}>What objects are allowed to be explored?</Text>
      
      <ScrollView contentContainerStyle={styles.list}>
        {categories.map(cat => {
          const isActive = selectedCats.has(cat.id);
          return (
            <TouchableOpacity 
              key={cat.id}
              style={[styles.card, isActive && styles.activeCard]}
              onPress={() => toggleCategory(cat.id)}
            >
              <Text style={[styles.cardTitle, isActive && styles.activeTitle]}>{cat.title}</Text>
            </TouchableOpacity>
          );
        })}
      </ScrollView>

      <PrimaryButton 
        label="Continue" 
        disabled={selectedCats.size === 0}
        onPress={() => navigation.navigate('DefaultMode')} 
        style={styles.button}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, padding: spacing.lg },
  header: { ...typography.h2, color: colors.textPrimary, marginTop: spacing.xl },
  subtext: { ...typography.body, color: colors.textSecondary, marginBottom: spacing.lg },
  list: { gap: spacing.md, paddingBottom: spacing.xxl },
  card: {
    padding: spacing.md,
    borderRadius: radii.md,
    borderWidth: 2,
    borderColor: colors.border,
    backgroundColor: colors.surface,
  },
  activeCard: { borderColor: colors.learn, backgroundColor: colors.learnLight },
  cardTitle: { ...typography.h3, color: colors.textPrimary },
  activeTitle: { color: colors.learn },
  button: { marginBottom: spacing.xl }
});

export default CategoryScreen;
