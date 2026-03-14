import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import { colors, spacing, typography, radii } from '../../theme/theme';
import { PrimaryButton } from '../../components/PrimaryButton';
import { ModeCard } from '../../components/ModeCard';
import { bootstrapAppSession } from '../../api/bootstrap';
import { updateCurrentSession, updateSettings } from '../../api/endpoints';
import { ChildSettings } from '../../types/settings';

const modeOptions: Array<{
  id: ChildSettings['defaultMode'];
  title: string;
  description: string;
}> = [
  { id: 'story', title: 'Story Mode', description: 'Magical object stories and narration' },
  { id: 'learn', title: 'Learn Mode', description: 'Simple words and toddler facts' },
  { id: 'explorer', title: 'Explorer Mode', description: 'Playful discovery prompts' },
];

const voiceOptions: Array<{
  id: ChildSettings['voiceStyle'];
  title: string;
  description: string;
}> = [
  { id: 'friendly_cartoon', title: 'Friendly Cartoon', description: 'Energetic and playful tone' },
  { id: 'story_narrator', title: 'Story Narrator', description: 'Calming and warm storytelling voice' },
];

const SettingsScreen = ({ navigation }: any) => {
  const [selectedMode, setSelectedMode] = useState<ChildSettings['defaultMode']>('story');
  const [selectedVoice, setSelectedVoice] = useState<ChildSettings['voiceStyle']>('friendly_cartoon');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const { session, settings } = await bootstrapAppSession();
        if (!mounted) return;
        setSelectedMode(session.active_mode || settings.defaultMode);
        setSelectedVoice(session.voice_style || settings.voiceStyle);
      } finally {
        if (mounted) setLoading(false);
      }
    };
    load();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
        alwaysBounceVertical={true}
        bounces={true}
        scrollEnabled={true}
        showsVerticalScrollIndicator={true}
      >
        <Text style={styles.title}>Settings</Text>
        <Text style={styles.subtitle}>Choose the mode and voice the app should use right now.</Text>
        <Text style={styles.sectionTitle}>Current Mode</Text>
        <View style={styles.list}>
          {modeOptions.map(mode => (
            <ModeCard
              key={mode.id}
              mode={mode.id}
              title={mode.title}
              description={mode.description}
              isActive={selectedMode === mode.id}
              onPress={() => setSelectedMode(mode.id)}
            />
          ))}
        </View>
        <Text style={styles.sectionTitle}>Voice Style</Text>
        <View style={styles.voiceList}>
          {voiceOptions.map(voice => {
            const isActive = selectedVoice === voice.id;
            return (
              <TouchableOpacity
                key={voice.id}
                style={[styles.voiceCard, isActive && styles.voiceCardActive]}
                onPress={() => setSelectedVoice(voice.id)}
                activeOpacity={0.8}
              >
                <Text style={[styles.voiceTitle, isActive && styles.voiceTitleActive]}>{voice.title}</Text>
                <Text style={styles.voiceDescription}>{voice.description}</Text>
                {isActive ? <Text style={styles.voiceBadge}>Selected</Text> : null}
              </TouchableOpacity>
            );
          })}
        </View>
        <PrimaryButton
          label={loading ? 'Loading...' : saving ? 'Saving...' : 'Save Settings'}
          disabled={loading || saving}
          onPress={async () => {
            setSaving(true);
            try {
              await updateSettings({ defaultMode: selectedMode, voiceStyle: selectedVoice });
              await updateCurrentSession({ active_mode: selectedMode, voice_style: selectedVoice });
              navigation.goBack();
            } finally {
              setSaving(false);
            }
          }}
          style={styles.button}
        />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scroll: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    flexGrow: 1,
    padding: spacing.xl,
    paddingBottom: spacing.xxl,
  },
  title: {
    ...typography.h1,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
    marginTop: spacing.xl,
  },
  subtitle: {
    ...typography.body,
    color: colors.textSecondary,
    marginBottom: spacing.xl,
    lineHeight: 24,
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  list: {
    marginBottom: spacing.xl,
  },
  voiceList: {
    marginBottom: spacing.xl,
    gap: spacing.md,
  },
  voiceCard: {
    backgroundColor: colors.surface,
    borderRadius: radii.md,
    padding: spacing.lg,
    borderWidth: 2,
    borderColor: colors.border,
  },
  voiceCardActive: {
    borderColor: colors.primary,
    backgroundColor: colors.storyLight,
  },
  voiceTitle: {
    ...typography.h3,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  voiceTitleActive: {
    color: colors.primaryActive,
  },
  voiceDescription: {
    ...typography.body,
    color: colors.textSecondary,
  },
  voiceBadge: {
    marginTop: spacing.sm,
    color: colors.primary,
    fontWeight: '700',
  },
  button: {
    width: '100%',
    marginBottom: spacing.xl,
  }
});

export default SettingsScreen;
