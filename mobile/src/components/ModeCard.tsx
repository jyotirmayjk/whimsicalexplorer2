import React from 'react';
import { TouchableOpacity, Text, StyleSheet, View } from 'react-native';
import { colors, spacing, typography } from '../theme/theme';

export type AppMode = 'story' | 'learn' | 'explorer';

interface ModeCardProps {
  mode: AppMode | string;
  title: string;
  description: string;
  isActive: boolean;
  onPress: () => void;
}

export const ModeCard: React.FC<ModeCardProps> = ({ mode, title, description, isActive, onPress }) => {
  return (
    <TouchableOpacity 
      style={[styles.card, isActive && styles.cardActive]} 
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.content}>
        <Text style={[styles.title, isActive && styles.titleActive]}>{title}</Text>
        <Text style={styles.description}>{description}</Text>
      </View>
      {isActive && (
        <View style={styles.activeIndicator}>
          <Text style={styles.activeText}>✓ Active</Text>
        </View>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: spacing.md,
    padding: spacing.lg,
    marginVertical: spacing.sm,
    borderWidth: 2,
    borderColor: colors.border,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  cardActive: {
    borderColor: colors.primary,
    backgroundColor: `${colors.primary}10`, // light tint
  },
  content: {
    marginBottom: spacing.sm,
  },
  title: {
    ...typography.h2,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  titleActive: {
    color: colors.primary,
  },
  description: {
    ...typography.body,
    color: colors.textSecondary,
    lineHeight: 22,
  },
  activeIndicator: {
    alignSelf: 'flex-start',
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: spacing.sm,
    marginTop: spacing.sm,
  },
  activeText: {
    color: colors.white,
    fontWeight: 'bold',
    fontSize: 12,
  }
});
