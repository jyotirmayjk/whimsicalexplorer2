import React, { useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { PrimaryButton } from '../../components/PrimaryButton';
import { ModeCard, AppMode } from '../../components/ModeCard';
import { colors, spacing, typography } from '../../theme/theme';

const DefaultModeScreen = ({ navigation }: any) => {
  const [selectedMode, setSelectedMode] = useState<AppMode | null>(null);

  const completeOnboarding = () => {
    // Navigate back up to RootNavigator to swap out Onboarding for MainTabs
    // Typically managed via App context/state, bypassing for skeleton scope natively via navigate
    navigation.reset({
      index: 0,
      routes: [{ name: 'MainTabs' }],
    });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Choose Default Mode</Text>
      <Text style={styles.subtext}>What mode should start on boot?</Text>
      
      <View style={styles.list}>
        <ModeCard 
          mode="story"
          title="Story Mode"
          description="Magical object stories and narration"
          isActive={selectedMode === 'story'}
          onPress={() => setSelectedMode('story')}
        />
        <ModeCard 
          mode="learn"
          title="Learn Mode"
          description="Simple words and toddler facts"
          isActive={selectedMode === 'learn'}
          onPress={() => setSelectedMode('learn')}
        />
        <ModeCard 
          mode="explorer"
          title="Explorer Mode"
          description="Playful discovery prompts"
          isActive={selectedMode === 'explorer'}
          onPress={() => setSelectedMode('explorer')}
        />
      </View>

      <PrimaryButton 
        label="Finish Setup" 
        disabled={!selectedMode}
        onPress={completeOnboarding} 
        style={styles.button}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, padding: spacing.lg },
  header: { ...typography.h2, color: colors.textPrimary, marginTop: spacing.xl },
  subtext: { ...typography.body, color: colors.textSecondary, marginBottom: spacing.lg },
  list: { flex: 1 },
  button: { marginBottom: spacing.xl }
});

export default DefaultModeScreen;
