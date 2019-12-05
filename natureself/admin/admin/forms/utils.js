import _ from 'lodash'

function buildFormdata (schema, initialData) {
  // build formdata based on schema, and populate with initialData
  if (!schema || !initialData) {
    return null
  }

  const formdata = {}
  const panels = getDataPanels(schema)
  panels.forEach(panel => {
    formdata[panel.form_field_name] = panel.options.default_value

    let initialValue = initialData[panel.field_name]
    if (initialValue !== undefined) {
      formdata[panel.form_field_name] = initialValue
    }
  })

  return formdata
}

function prepareSubmitFormdata (schema, formdata) {
  if (!formdata || !schema) {
    return {}
  }

  const newFormdata = {}
  const panels = getDataPanels(schema)
  panels.forEach(panel => {
    let newValue = formdata[panel.form_field_name]
    if (newValue !== undefined) {
      if (panel.form_field_property) {
        if (panel.many_field) {
          newValue = _.map(newValue, panel.form_field_property)
        } else {
          // newValue could be null, e.g. empty picture
          newValue = newValue ? newValue[panel.form_field_property] : null
        }
      }
      newFormdata[panel.form_field_name] = newValue
    }
  })
  return newFormdata
}

function getDataPanels (schema, childrenAttr) {
  // get all data panels from form schema
  let panels = []

  let children = childrenAttr === undefined ? schema.panels : schema[childrenAttr]
  children.forEach(panel => {
    if (panel.data_panel) {
      panels.push(panel)
    } else if (panel.panels) {
      panels = panels.concat(getDataPanels(panel))
    } else if (panel.tabs) {
      panel.tabs.forEach(tab => {
        panels = panels.concat(getDataPanels(tab))
      })
    }
  })

  return panels
}

export default {
  buildFormdata,
  prepareSubmitFormdata,
}
