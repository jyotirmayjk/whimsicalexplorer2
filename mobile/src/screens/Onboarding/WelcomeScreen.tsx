import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { PrimaryButton } from '../../components/PrimaryButton';
import { colors, spacing, typography } from '../../theme/theme';
import { ensureLogin } from '../../api/endpoints';

const WelcomeScreen = ({ navigation }: any) => {
  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Kids Pokédex</Text>
        <Text style={styles.subtitle}>
          The safest AI companion for your child to explore, learn, and imagine the world around them.
        </Text>
      </View>
      <PrimaryButton 
        label="Get Started" 
        onPress={async () => {
          await ensureLogin();
          navigation.navigate('VoiceStyle');
        }} 
        style={styles.button}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: spacing.xl,
    justifyContent: 'space-between',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    ...typography.h1,
    color: colors.primary,
    marginBottom: spacing.md,
    textAlign: 'center',
  },
  subtitle: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 24,
  },
  button: {
    marginBottom: spacing.xl,
  }
});

export default WelcomeScreen;
