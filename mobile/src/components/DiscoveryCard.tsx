import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity } from 'react-native';
import { colors, spacing, radii, typography } from '../theme/theme';

interface DiscoveryCardProps {
  name: string;
  category: string;
  imageUrl?: string;
  timestamp: string;
  onPress: () => void;
  onReplay?: () => void;
  onFavorite?: () => void;
}

export const DiscoveryCard: React.FC<DiscoveryCardProps> = ({
  name,
  category,
  imageUrl,
  timestamp,
  onPress,
}) => {
  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.9}>
      <View style={styles.imagePlaceholder}>
        {/* Placeholder for Object Storage Image */}
      </View>
      <View style={styles.content}>
        <Text style={styles.name}>{name}</Text>
        <Text style={styles.category}>{category}</Text>
        <Text style={styles.time}>{timestamp}</Text>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: radii.md,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: spacing.md,
    flex: 1,
  },
  imagePlaceholder: {
    height: 120,
    backgroundColor: colors.explorerLight,
  },
  content: {
    padding: spacing.sm,
  },
  name: {
    ...typography.h3,
    color: colors.textPrimary,
  },
  category: {
    ...typography.caption,
    color: colors.learn,
    marginTop: 2,
  },
  time: {
    ...typography.caption,
    color: colors.textSecondary,
    fontSize: 12,
    marginTop: spacing.xs,
  }
});
