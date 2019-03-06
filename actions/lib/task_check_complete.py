import base_action


class TaskCheckComplete(base_action.BaseAction):

    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(TaskCheckComplete, self).__init__(config)

    def task_check_complete(self, client, kwargs_dict):
        """Check if a given task is complete and fail if it isn't
        :param client: connection from the base_action
        :param kwargs_dict:
        """
        id = self._get_arg("task_id", kwargs_dict)
        task = client.collections.tasks(id)

        if(task.state.lower() != 'finished'):
            raise RuntimeError('The MIQ task is not finished executing!')

        return True
