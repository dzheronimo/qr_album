'use client';

import { useState } from 'react';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { MarketingShell } from '@/components/marketing/MarketingShell';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

const schema = z.object({
  name: z.string().min(2, 'Имя должно содержать минимум 2 символа'),
  email: z.string().email('Введите корректный email'),
  subject: z.string().min(5, 'Тема должна содержать минимум 5 символов'),
  message: z.string().min(10, 'Сообщение должно содержать минимум 10 символов'),
});

type ContactForm = z.infer<typeof schema>;

export default function ContactPage() {
  const [sent, setSent] = useState(false);
  const { register, handleSubmit, formState: { errors }, reset } = useForm<ContactForm>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async () => {
    setSent(true);
    reset();
  };

  return (
    <MarketingShell
      title="Свяжитесь с нами"
      subtitle="Ответим по продукту, тарифам и интеграции в течение рабочего дня"
    >
      <Card>
        <CardContent className="pt-6">
          <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
            <Input placeholder="Ваше имя" {...register('name')} name="name" />
            {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}

            <Input placeholder="Email" type="email" {...register('email')} name="email" />
            {errors.email && <p className="text-sm text-destructive">{errors.email.message}</p>}

            <Input placeholder="Тема" {...register('subject')} name="subject" />
            {errors.subject && <p className="text-sm text-destructive">{errors.subject.message}</p>}

            <Textarea placeholder="Сообщение" {...register('message')} name="message" />
            {errors.message && <p className="text-sm text-destructive">{errors.message.message}</p>}

            <Button type="submit">Отправить</Button>
          </form>

          {sent && (
            <p className="mt-4 text-green-600 font-medium">Сообщение отправлено</p>
          )}
        </CardContent>
      </Card>
    </MarketingShell>
  );
}
