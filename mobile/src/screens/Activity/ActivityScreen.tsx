import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, spacing, typography, radii } from '../../theme/theme';

const ActivityScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.header}>Activity Timeline</Text>
      
      <View style={styles.timelineChunk}>
         <View style={styles.timelineNode} />
         <View style={styles.timelineContent}>
            <Text style={styles.time}>10:00 AM</Text>
            <Text style={styles.action}>Spoke with Teddy Bear in Story Mode</Text>
         </View>
      </View>

      <View style={styles.timelineChunk}>
         <View style={styles.timelineNode} />
         <View style={styles.timelineContent}>
            <Text style={styles.time}>9:45 AM</Text>
            <Text style={styles.action}>Discovered Teddy Bear</Text>
         </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, padding: spacing.lg },
  header: { ...typography.h1, color: colors.textPrimary, marginBottom: spacing.xl },
  timelineChunk: {
    flexDirection: 'row',
    marginBottom: spacing.xl,
  },
  timelineNode: {
    width: 16,
    height: 16,
    borderRadius: radii.round,
    backgroundColor: colors.primary,
    marginTop: 4,
    marginRight: spacing.md,
  },
  timelineContent: {
    flex: 1,
  },
  time: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  action: {
    ...typography.body,
    color: colors.textPrimary,
  }
});

export default ActivityScreen;
