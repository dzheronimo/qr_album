import { redirect } from 'next/navigation';

export default function DocsPage() {
  // Редирект на страницу помощи
  redirect('/help');
}
