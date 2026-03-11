import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { colors, spacing, typography } from '../../theme/theme';
import { ModeCard } from '../../components/ModeCard';
import { DiscoveryCard } from '../../components/DiscoveryCard';
import { PrimaryButton } from '../../components/PrimaryButton';

const HomeScreen = ({ navigation }: any) => {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.greeting}>Hi there! 👋</Text>
        <Text style={styles.subGreeting}>Let's explore the world today.</Text>
      </View>

      <Text style={styles.sectionTitle}>Current Mode</Text>
      <ModeCard
        mode="story"
        title="Story Mode"
        description="Magical object stories and narration"
        isActive={true}
        onPress={() => {}}
      />

      <PrimaryButton 
        label="Change Mode" 
        onPress={() => navigation.navigate('Settings')} 
        style={styles.changeModeBtn}
      />

      <View style={styles.recentSection}>
        <Text style={styles.sectionTitle}>Recent Discoveries</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.rail}>
          <View style={styles.cardWrapper}>
             <DiscoveryCard 
                name="Red Fire Truck" 
                category="Vehicles" 
                timestamp="2 hours ago" 
                onPress={() => navigation.navigate('Discoveries')} 
             />
          </View>
          <View style={styles.cardWrapper}>
             <DiscoveryCard 
                name="Golden Retriever" 
                category="Animals" 
                timestamp="Yesterday" 
                onPress={() => navigation.navigate('Discoveries')} 
             />
          </View>
        </ScrollView>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.lg, paddingBottom: spacing.xxl },
  header: { marginBottom: spacing.xl, marginTop: spacing.md },
  greeting: { ...typography.h1, color: colors.textPrimary },
  subGreeting: { ...typography.body, color: colors.textSecondary, marginTop: spacing.xs },
  sectionTitle: { ...typography.h3, color: colors.textPrimary, marginBottom: spacing.sm, marginTop: spacing.lg },
  changeModeBtn: { marginTop: spacing.sm, backgroundColor: colors.surface },
  recentSection: { marginTop: spacing.xl },
  rail: { paddingRight: spacing.lg },
  cardWrapper: { width: 160, marginRight: spacing.md }
});

export default HomeScreen;
