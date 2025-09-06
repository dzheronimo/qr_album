import { redirect } from 'next/navigation';

export default function AdminPage() {
  // Redirect to dashboard by default
  redirect('/dashboard');
}


