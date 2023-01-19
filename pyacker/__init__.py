import os

import requests
from basic_api import BasicAPI

HCP_OAUTH_URL = "https://auth.hashicorp.com/oauth/token"
HCP_OAUTH_AUDIENCE = "https://api.hashicorp.cloud"
HCP_BASE_URL = "https://api.cloud.hashicorp.com"
PACKER_BASE_URL = f"{HCP_BASE_URL}/packer/2021-04-30"


class Pyacker:
    def __init__(
        self,
        organization_id: str = None,
        project_id: str = None,
        client_id: str = None,
        client_secret: str = None,
        base_url: str = PACKER_BASE_URL,
    ):
        self.organization_id = os.getenv("HCP_ORGANIZATION_ID", organization_id)
        self.project_id = os.getenv("HCP_PROJECT_ID", project_id)
        self.client_id = os.getenv("HCP_CLIENT_ID", client_id)
        self._client_secret = os.getenv("HCP_CLIENT_SECRET", client_secret)
        self._base_url = f"{base_url}/organizations/{self.organization_id}/projects/{self.project_id}"
        self._token = None
        self.client = BasicAPI(self._base_url)

    def auth(
        self, oauth_url: str = HCP_OAUTH_URL, audience: str = HCP_OAUTH_AUDIENCE
    ) -> requests.Response:
        auth_resp = requests.post(
            url=oauth_url,
            data=dict(
                grant_type="client_credentials",
                client_id=self.client_id,
                client_secret=self._client_secret,
                audience=audience,
            ),
        )
        auth_resp.raise_for_status()
        self._token = auth_resp.json()["access_token"]
        self.client = BasicAPI(
            self._base_url, headers={"Authorization": f"Bearer {self._token}"}
        )
        return auth_resp

    def __getattr__(self, name):
        if client_attr := getattr(self.client, name, None):
            return client_attr
        raise AttributeError(f"{self.__class__} does not have `{name}` attribute.")

    def create_bucket(
        self,
    ):
        """Creates an image bucket in the HCP Packer registry."""
        raise NotImplementedError

    def create_build(self, bucket_slug, iteration_id):
        """Creates an image build in the provided image iteration.
            It is called once for each \"build source\" in a Packer build run.
            The request will error if the build for a given cloud provider already exists.

        :param str bucket_slug: Human-readable name for the bucket. (required)
        :param str iteration_id: ULID of the iteration that this build should be associated with. (required)

        """
        raise NotImplementedError

    def create_channel(self, bucket_slug):
        """Creates a channel either empty or assigned to an iteration.

        :param str bucket_slug: Human-readable name for the bucket to associate the channel with. (required)
        """
        raise NotImplementedError

    def create_iteration(self, bucket_slug):
        """Creates an empty iteration to be written to. This API is called at
            the beginning of a new Packer build and does not create individual builds
            for the iteration.

        :param str bucket_slug: Human-readable name for the bucket. (required)
        """
        raise NotImplementedError

    def create_registry(
        self,
    ):
        """Creates a HCP Packer registry and starts billing for it."""
        raise NotImplementedError

    def delete_bucket(self, bucket_slug):
        """Deletes a bucket and all its information, such as iterations and builds.


        :param str bucket_slug: Human-readable name for the bucket. (required)
        """
        raise NotImplementedError

    def delete_build(self, build_id):
        """Deletes a build in the provided iteration.

        :param str build_id: ULID of the build that should be deleted. (required)
        """
        raise NotImplementedError

    def delete_channel(self, bucket_slug, slug):
        """Deletes a channel.

        :param str bucket_slug: Human-readable name for the bucket that the channel
            is associated with. (required)
        :param str slug: Human-readable name for the channel. (required)
        """
        raise NotImplementedError

    def delete_iteration(self, iteration_id):
        """Deletes an iteration and all its information, such as its builds.

        :param str iteration_id: ULID of the iteration. This was created and set
            by the HCP Packer registry when the iteration was created. (required)
        """
        raise NotImplementedError

    def delete_registry(self):
        """Deactivates an active HCP packer registry.
            Deactivating a registry will stop any additional billing for the resource.
            Setting the `hard_delete` param to true will delete the registry and any
            associated resources from the database.

        :param bool hard_delete: When set to true, the registry will be deleted
            from database and recovery will no longer be possible.
        """
        raise NotImplementedError

    def get_bucket(self, bucket_slug, bucket_id=None):
        """Gets a bucket with its latest completed iteration.

        :param str bucket_slug: Human-readable name for the bucket. (required)
        :param str bucket_id: ULID of the bucket.
        """
        response = self.client.get.images[bucket_slug]()
        response.raise_for_status()
        return response.json()

    def get_build(self, build_id):
        """Gets a build with its list of images.

        :param str build_id: ULID of the build that should be retrieved. (required)

        """
        raise NotImplementedError

    def get_channel(self, bucket_slug, slug):
        """Gets a channel with the iteration that it is currently assigned if any.

        :param str bucket_slug: Human-readable name for the bucket that the
            channel is associated with. (required)
        :param str slug: Human-readable name for the channel. (required)
        """
        raise NotImplementedError

    def get_iteration(self, bucket_slug):
        """Allows the user to get an iteration using one of the following identifiers:
            * iteration_id
            * incremental_version
            * fingerprint

            These are supplied as a query parameter (e.g. `images/{bucket_slug}/iteration?fingerprint={fingerprint}`).

        :param str bucket_slug: Human-readable name for the bucket. (required)
        :param int incremental_version: The human-readable version number assigned to this iteration.
        :param str iteration_id: ULID of the iteration.
        :param str fingerprint: Fingerprint of the iteration. The fingerprint
            is set by Packer when you call `packer build`. It will most often
            correspond to a git commit sha, but can be manually overridden by setting
            the environment variable `HCP_PACKER_BUILD_FINGERPRINT`.
        """
        raise NotImplementedError

    def get_registry(self):
        """Gets a HCP Packer registry."""
        raise NotImplementedError

    def get_registry_tfc_run_task_api(self, task_type):
        """Gets the HCP Packer registry API URL and HMAC key to integrate with Terraform Cloud as a Run Task.

        :param str task_type: The HCP Packer Terraform Cloud run task type.
            Currently, the only existing type is `validation`. (required)
        """
        raise NotImplementedError

    def list_buckets(self):
        """Lists every existing bucket in the HCP Packer registry and their last completed iteration.

        :param int pagination_page_size: The max number of results per page that should be returned.
            If the number of available results is larger than `page_size`, a `next_page_token` is
            returned which can be used to get the next page of results in subsequent requests.
            A value of zero will cause `page_size` to be defaulted.
        :param str pagination_next_page_token: Specifies a page token to use to retrieve the
            next page. Set this to the `next_page_token` returned by previous list requests to get
            the next page of results. If set, `previous_page_token` must not be set.
        :param str pagination_previous_page_token: Specifies a page token to use to retrieve
            the previous page. Set this to the `previous_page_token` returned by previous list
            requests to get the previous page of results. If set, `next_page_token` must not be set.
        :param list[str] sorting_order_by: Specifies the list of per field ordering
            that should be used for sorting.  The order matters as rows are sorted in order by
            fields and when the field matches, the next field is used to tie break the ordering.
            The per field default ordering is ascending.
            The fields should be immutable, unique, and orderable. If the field is not unique,
            more than one sort fields should be passed.
            Example: oder_by=name,age desc,created_at asc In that case, 'name' will get the default 'ascending' order.
        """
        response = self.client.get.images()
        response.raise_for_status()
        return response.json()["buckets"]

    def list_builds(self, bucket_slug, iteration_id):
        """Lists every existing build and its images for an iteration.

        :param str bucket_slug: Human-readable name for the bucket to list builds for. (required)
        :param str iteration_id: ULID of the iteration to list builds for. (required)
        :param int pagination_page_size: The max number of results per page that should be returned.
            If the number of available results is larger than `page_size`, a `next_page_token` is
            returned which can be used to get the next page of results in subsequent requests.
            A value of zero will cause `page_size` to be defaulted.
        :param str pagination_next_page_token: Specifies a page token to use to retrieve the
            next page. Set this to the `next_page_token` returned by previous list requests to get
            the next page of results. If set, `previous_page_token` must not be set.
        :param str pagination_previous_page_token: Specifies a page token to use to retrieve
            the previous page. Set this to the `previous_page_token` returned by previous list
            requests to get the previous page of results. If set, `next_page_token` must not be set.
        :param list[str] sorting_order_by: Specifies the list of per field ordering
            that should be used for sorting.  The order matters as rows are sorted in order by
            fields and when the field matches, the next field is used to tie break the ordering.
            The per field default ordering is ascending.
            The fields should be immutable, unique, and orderable. If the field is not unique,
            more than one sort fields should be passed.
            Example: oder_by=name,age desc,created_at asc In that case, 'name' will get the default 'ascending' order.
        """
        raise NotImplementedError

    def list_channels(self, bucket_slug):
        """Lists all channels of a given bucket.

        :param str bucket_slug: Human-readable name for the bucket you want to list channels for. (required)
        """
        raise NotImplementedError

    def list_iterations(self, bucket_slug):
        """Lists every existing iteration of a bucket.

        :param str bucket_slug: Human-readable name for the bucket. (required)
        :param int pagination_page_size: The max number of results per page that should be returned.
            If the number of available results is larger than `page_size`, a `next_page_token` is
            returned which can be used to get the next page of results in subsequent requests.
            A value of zero will cause `page_size` to be defaulted.
        :param str pagination_next_page_token: Specifies a page token to use to retrieve the
            next page. Set this to the `next_page_token` returned by previous list requests to get
            the next page of results. If set, `previous_page_token` must not be set.
        :param str pagination_previous_page_token: Specifies a page token to use to retrieve
            the previous page. Set this to the `previous_page_token` returned by previous list
            requests to get the previous page of results. If set, `next_page_token` must not be set.
        :param list[str] sorting_order_by: Specifies the list of per field ordering
            that should be used for sorting.  The order matters as rows are sorted in order by
            fields and when the field matches, the next field is used to tie break the ordering.
            The per field default ordering is ascending.
            The fields should be immutable, unique, and orderable. If the field is not unique,
            more than one sort fields should be passed.
            Example: oder_by=name,age desc,created_at asc In that case, 'name' will get the default 'ascending' order."""
        raise NotImplementedError

    def regenerate_tfc_run_task_hmac_key(
        self,
    ):
        """Regenerates the HMAC key used to sign requests from Terraform Cloud to HCP Packer run tasks."""
        raise NotImplementedError

    def update_bucket(self, bucket_slug):
        """Updates a bucket's information.

        :param str bucket_slug: Human-readable name for the bucket. (required)
        """
        raise NotImplementedError

    def update_build(self, build_id):
        """Updates an image build. This may be most often used for modifying the status of a currently running build.

        :param str build_id: ULID of the build that should be updated. (required)

        """
        raise NotImplementedError

    def update_channel(self, bucket_slug, slug):
        """Updates a channel to clear or point to a new iteration.

        :param str bucket_slug: Human-readable name for the bucket that the channel is associated with. (required)
        :param str slug: Human-readable name for the channel. (required)
        :return:
        """
        raise NotImplementedError

    def update_iteration(self, iteration_id):
        """This API can be used to revoke, restore, or complete an iteration.
            Revoking can be done at any time to complete or incomplete iterations,
            immediately or in the future depending on the passing timestamp.
            Revoked iterations cannot be updated unless restored.
            To make build-specific updates for builds within the iteration, use
            the Update Build endpoint.

        :param str iteration_id: ULID of the iteration. (required)
        :return:
        """

        raise NotImplementedError

    def update_registry(self):
        """Updates the feature tier of an HCP Packer registry."""

        raise NotImplementedError
