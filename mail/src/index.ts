import { serve } from '@hono/node-server'
import { Hono } from 'hono'
import { renderToStaticMarkup } from '@usewaypoint/email-builder'

const app = new Hono()

app.get('/template/:configuration', (c) => {
  const encodedConfiguration = c.req.param('configuration') // base64 encoded
  const configuration = JSON.parse(decodeURIComponent(Buffer.from(encodedConfiguration, 'base64').toString('utf-8')))
  const template = renderToStaticMarkup(configuration, { rootBlockId: 'root' })
  return c.html(template)
})

serve({
  fetch: app.fetch,
  port: 3000
}, (info) => {
  console.log(`Server is running on http://localhost:${info.port}`)
})
