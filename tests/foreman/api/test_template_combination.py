"""Tests for template combination

:Requirement: TemplateCombination

:CaseAutomation: Automated

:CaseLevel: Component

:CaseComponent: ProvisioningTemplates

:Assignee: rplevka

:TestType: Functional

:Upstream: No
"""
import pytest
from nailgun import entities
from requests.exceptions import HTTPError


@pytest.fixture(scope='module')
def module_hostgroup_and_environment(module_hostgroup, module_env):
    """Create hostgroup and environment to be used on
    TemplateCombination creation
    """
    yield {'hostgroup': module_hostgroup, 'env': module_env}
    # Delete hostgroup and environment used on TemplateCombination creation
    for entity in (module_hostgroup, module_env):
        entity.delete()


@pytest.fixture(scope='function')
def function_template_combination(module_hostgroup_and_environment):
    """Create ProvisioningTemplate and TemplateConfiguration for each test
    and at the end delete ProvisioningTemplate used on tests
    """
    template = entities.ProvisioningTemplate(
        snippet=False,
        template_combinations=[
            {
                'hostgroup_id': module_hostgroup_and_environment['hostgroup'].id,
                'environment_id': module_hostgroup_and_environment['env'].id,
            }
        ],
    )
    template = template.create()
    template_combination_dct = template.template_combinations[0]
    template_combination = entities.TemplateCombination(
        id=template_combination_dct['id'],
        environment=module_hostgroup_and_environment['env'],
        provisioning_template=template,
        hostgroup=module_hostgroup_and_environment['hostgroup'],
    )
    yield {'template': template, 'template_combination': template_combination}
    # Clean combination if it is not already deleted
    try:
        template_combination.delete()
    except HTTPError:
        pass
    template.delete()


@pytest.mark.tier1
def test_positive_get_combination(function_template_combination, module_hostgroup_and_environment):
    """Assert API template combination get method works.

    :id: 2447674e-c37e-11e6-93cb-68f72889dc7f

    :Setup: save a template combination

    :expectedresults: TemplateCombination can be retrieved through API

    :CaseImportance: Critical

    :BZ: 1369737
    """
    combination = function_template_combination['template_combination'].read()
    assert isinstance(combination, entities.TemplateCombination)
    assert function_template_combination['template'].id == combination.provisioning_template.id
    assert module_hostgroup_and_environment['env'].id == combination.environment.id
    assert module_hostgroup_and_environment['hostgroup'].id == combination.hostgroup.id


@pytest.mark.tier1
@pytest.mark.upgrade
def test_positive_delete_combination(function_template_combination):
    """Assert API template combination delete method works.

    :id: 3a5cb370-c5f6-11e6-bb2f-68f72889dc7f

    :Setup: save a template combination

    :expectedresults: TemplateCombination can be deleted through API

    :CaseImportance: Critical

    :BZ: 1369737
    """
    combination = function_template_combination['template_combination'].read()
    assert isinstance(combination, entities.TemplateCombination)
    assert 1 == len(function_template_combination['template'].read().template_combinations)
    combination.delete()
    with pytest.raises(HTTPError):
        combination.read()
    assert 0 == len(function_template_combination['template'].read().template_combinations)
