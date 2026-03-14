import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { colors, spacing, typography } from '../../theme/theme';
import { ModeCard } from '../../components/ModeCard';
import { DiscoveryCard } from '../../components/DiscoveryCard';
import { PrimaryButton } from '../../components/PrimaryButton';
import { bootstrapAppSession } from '../../api/bootstrap';

const modeCopy = {
  story: {
    title: 'Story Mode',
    description: 'Magical object stories and narration',
  },
  learn: {
    title: 'Learn Mode',
    description: 'Simple words and toddler facts',
  },
  explorer: {
    title: 'Explorer Mode',
    description: 'Playful discovery prompts',
  },
} as const;

const HomeScreen = ({ navigation }: any) => {
  const [currentMode, setCurrentMode] = useState<'story' | 'learn' | 'explorer'>('story');
  const [loadingMode, setLoadingMode] = useState(true);

  const loadCurrentMode = React.useCallback(async () => {
    setLoadingMode(true);
    try {
      const { session, settings } = await bootstrapAppSession();
      setCurrentMode(session.active_mode || settings.defaultMode);
    } catch (_error) {
      setCurrentMode('story');
    } finally {
      setLoadingMode(false);
    }
  }, []);

  useEffect(() => {
    loadCurrentMode();
  }, [loadCurrentMode]);

  useFocusEffect(
    React.useCallback(() => {
      loadCurrentMode();
    }, [loadCurrentMode]),
  );

  const currentModeCopy = modeCopy[currentMode];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.greeting}>Hi there! 👋</Text>
        <Text style={styles.subGreeting}>Let's explore the world today.</Text>
      </View>

      <Text style={styles.sectionTitle}>Current Mode</Text>
      <ModeCard
        mode={currentMode}
        title={loadingMode ? 'Loading Mode...' : currentModeCopy.title}
        description={loadingMode ? 'Fetching backend session state' : currentModeCopy.description}
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
