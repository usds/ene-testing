FROM rails
RUN /usr/sbin/groupadd usds -g 900
RUN /usr/sbin/useradd -rm -d /home/usds -s /bin/bash -g usds -G sudo -u 900 usds
WORKDIR "/home/usds"
RUN git clone https://github.com/HHSIDEAlab/medicaid_eligibility
WORKDIR "/home/usds/medicaid_eligibility"
RUN bundle install
RUN rake test
RUN chown -R usds:usds /home/usds
USER usds
EXPOSE 3000
CMD rails s