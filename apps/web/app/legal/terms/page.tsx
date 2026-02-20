import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Условия использования | QR Album',
  description: 'Условия использования сервиса QR Album',
};

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow-lg rounded-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">
            Условия использования
          </h1>
          
          <div className="prose prose-lg max-w-none">
            <p className="text-gray-600 mb-6">
              Последнее обновление: {new Date().toLocaleDateString('ru-RU')}
            </p>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                1. Принятие условий
              </h2>
              <p className="text-gray-700 mb-4">
                Используя сервис QR Album, вы соглашаетесь с данными условиями использования. 
                Если вы не согласны с какими-либо условиями, пожалуйста, не используйте наш сервис.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                2. Описание сервиса
              </h2>
              <p className="text-gray-700 mb-4">
                QR Album — это платформа для создания цифровых альбомов с QR-кодами, 
                позволяющая пользователям создавать, управлять и делиться своими альбомами.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                3. Регистрация и учетная запись
              </h2>
              <p className="text-gray-700 mb-4">
                Для использования сервиса вам необходимо создать учетную запись. 
                Вы обязуетесь предоставлять точную и актуальную информацию при регистрации.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                4. Использование сервиса
              </h2>
              <p className="text-gray-700 mb-4">
                Вы можете использовать QR Album только в законных целях. 
                Запрещается использовать сервис для:
              </p>
              <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
                <li>Нарушения законов или прав третьих лиц</li>
                <li>Распространения вредоносного контента</li>
                <li>Спама или нежелательных сообщений</li>
                <li>Попыток взлома или нарушения безопасности</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                5. Интеллектуальная собственность
              </h2>
              <p className="text-gray-700 mb-4">
                Вы сохраняете права на контент, который создаете с помощью QR Album. 
                Предоставляя нам лицензию на использование вашего контента для предоставления сервиса.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                6. Конфиденциальность
              </h2>
              <p className="text-gray-700 mb-4">
                Ваша конфиденциальность важна для нас. 
                Подробная информация о том, как мы обрабатываем ваши данные, 
                содержится в нашей Политике конфиденциальности.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                7. Ограничение ответственности
              </h2>
              <p className="text-gray-700 mb-4">
                QR Album предоставляется "как есть". Мы не гарантируем, 
                что сервис будет работать без ошибок или прерываний.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                8. Изменения условий
              </h2>
              <p className="text-gray-700 mb-4">
                Мы оставляем за собой право изменять данные условия в любое время. 
                Продолжение использования сервиса после изменений означает ваше согласие с новыми условиями.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                9. Контактная информация
              </h2>
              <p className="text-gray-700 mb-4">
                Если у вас есть вопросы по условиям или обработке данных, пишите: privacy@storyqr.ru, legal@storyqr.ru
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}

