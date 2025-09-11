import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Помощь | StoryQR',
  description: 'Получите помощь по использованию StoryQR',
};

export default function HelpPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">
            Помощь по StoryQR
          </h1>
          
          <div className="space-y-8">
            <section>
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                Как создать альбом
              </h2>
              <p className="text-gray-600">
                Перейдите в раздел "Альбомы" и нажмите "Создать альбом". 
                Заполните название и описание, затем добавьте страницы с QR-кодами.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                Как добавить QR-код
              </h2>
              <p className="text-gray-600">
                В созданном альбоме нажмите "Добавить страницу". 
                Загрузите медиафайлы и создайте QR-код для доступа к странице.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                Как поделиться альбомом
              </h2>
              <p className="text-gray-600">
                Используйте QR-коды для быстрого доступа к вашим страницам. 
                QR-коды можно скачать и распечатать.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                Техническая поддержка
              </h2>
              <p className="text-gray-600">
                Если у вас возникли вопросы, обратитесь в службу поддержки 
                или проверьте документацию.
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
