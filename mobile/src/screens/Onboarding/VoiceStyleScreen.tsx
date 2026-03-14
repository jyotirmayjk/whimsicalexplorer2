import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { PrimaryButton } from '../../components/PrimaryButton';
import { colors, spacing, typography, radii } from '../../theme/theme';
import { ChildSettings } from '../../types/settings';
import { updateSettings } from '../../api/endpoints';

const VoiceStyleScreen = ({ navigation }: any) => {
  const [selectedVoice, setSelectedVoice] = useState<ChildSettings['voiceStyle'] | null>(null);
  const [saving, setSaving] = useState(false);

  const voices = [
    { id: 'friendly_cartoon', title: 'Friendly Cartoon', desc: 'Energetic and playful tone' },
    { id: 'story_narrator', title: 'Story Narrator', desc: 'Calming and warm storytelling voice' }
  ];

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Choose a Voice Style</Text>
      <Text style={styles.subtext}>How should I sound when talking?</Text>
      
      <View style={styles.list}>
        {voices.map(voice => {
          const isActive = selectedVoice === voice.id;
          return (
            <TouchableOpacity 
              key={voice.id}
              style={[styles.card, isActive && styles.activeCard]}
              onPress={() => setSelectedVoice(voice.id as any)}
            >
              <Text style={[styles.cardTitle, isActive && styles.activeTitle]}>{voice.title}</Text>
              <Text style={styles.cardDesc}>{voice.desc}</Text>
            </TouchableOpacity>
          );
        })}
      </View>

      <PrimaryButton 
        label={saving ? 'Saving...' : 'Continue'} 
        disabled={!selectedVoice || saving}
        onPress={async () => {
          if (!selectedVoice) return;
          setSaving(true);
          try {
            await updateSettings({ voiceStyle: selectedVoice });
            navigation.navigate('CategorySelection');
          } finally {
            setSaving(false);
          }
        }} 
        style={styles.button}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, padding: spacing.lg },
  header: { ...typography.h2, color: colors.textPrimary, marginTop: spacing.xl },
  subtext: { ...typography.body, color: colors.textSecondary, marginBottom: spacing.lg },
  list: { flex: 1, gap: spacing.md },
  card: {
    padding: spacing.lg,
    borderRadius: radii.md,
    borderWidth: 2,
    borderColor: colors.border,
    backgroundColor: colors.surface,
  },
  activeCard: { borderColor: colors.primary, backgroundColor: colors.storyLight },
  cardTitle: { ...typography.h3, color: colors.textPrimary, marginBottom: spacing.xs },
  activeTitle: { color: colors.primaryActive },
  cardDesc: { ...typography.caption, color: colors.textSecondary },
  button: { marginBottom: spacing.xl }
});

export default VoiceStyleScreen;
