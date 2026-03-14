import { ensureLogin, getCurrentSession, getSettings, startSession } from './endpoints';
import { ChildSettings } from '../types/settings';

export const bootstrapAppSession = async (): Promise<{
  settings: ChildSettings;
  session: Awaited<ReturnType<typeof startSession>>;
}> => {
  await ensureLogin();
  const settings = await getSettings();

  try {
    const session = await getCurrentSession();
    return { settings, session };
  } catch (_error) {
    const session = await startSession({});
    return { settings, session };
  }
};
