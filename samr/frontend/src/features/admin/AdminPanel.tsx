import * as Tabs from '@radix-ui/react-tabs';
import { CentersTab } from './CentersTab';
import { DevicesTab } from './DevicesTab';
import { FaqTab } from './FaqTab';

export function AdminPanel() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Administración</h1>
        <p className="text-gray-600 text-sm">Centros médicos, dispositivos IoT y FAQ del chatbot.</p>
      </div>

      <Tabs.Root defaultValue="centers">
        <Tabs.List className="flex border-b border-gray-200 mb-4">
          <Tabs.Trigger
            value="centers"
            className="px-4 py-2 text-sm font-medium text-gray-500 border-b-2 border-transparent data-[state=active]:border-teal-600 data-[state=active]:text-teal-700"
          >
            Centros
          </Tabs.Trigger>
          <Tabs.Trigger
            value="devices"
            className="px-4 py-2 text-sm font-medium text-gray-500 border-b-2 border-transparent data-[state=active]:border-teal-600 data-[state=active]:text-teal-700"
          >
            Dispositivos
          </Tabs.Trigger>
          <Tabs.Trigger
            value="faq"
            className="px-4 py-2 text-sm font-medium text-gray-500 border-b-2 border-transparent data-[state=active]:border-teal-600 data-[state=active]:text-teal-700"
          >
            FAQ
          </Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="centers"><CentersTab /></Tabs.Content>
        <Tabs.Content value="devices"><DevicesTab /></Tabs.Content>
        <Tabs.Content value="faq"><FaqTab /></Tabs.Content>
      </Tabs.Root>
    </div>
  );
}
