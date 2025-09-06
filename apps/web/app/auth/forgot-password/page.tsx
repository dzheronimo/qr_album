import { Metadata } from 'next';
import Link from 'next/link';
import { redirect } from 'next/navigation';

export const metadata: Metadata = {
  title: 'Восстановление пароля | StoryQR',
  description: 'Восстановите доступ к вашему аккаунту StoryQR. Введите email для получения инструкций по сбросу пароля.',
};

export default function ForgotPasswordPage() {
  // Редирект на страницу сброса пароля
  redirect('/auth/reset-password');
}
